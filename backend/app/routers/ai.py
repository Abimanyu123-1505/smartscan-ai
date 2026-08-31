import json
import datetime as dt
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..services.audit import log_action

router = APIRouter(prefix="/api/v1", tags=["ai"])


def _build_case_context(db: Session, case_id: str) -> dict:
    """Build a rich context dict from all case data for RAG."""
    case = db.get(models.Case, case_id)
    if not case:
        return {}
    evidence = db.query(models.Evidence).filter(models.Evidence.case_id == case_id).all()
    artifacts = db.query(models.Artifact).filter(models.Artifact.case_id == case_id).limit(100).all()
    flagged = [a for a in artifacts if a.flagged_score > 0]
    yara = db.query(models.YARAMatch).filter(models.YARAMatch.case_id == case_id).all()
    sigma = db.query(models.SigmaAlert).filter(models.SigmaAlert.case_id == case_id).all()
    ioc_matches = db.query(models.IOCMatch).filter(models.IOCMatch.case_id == case_id).all()
    memory = db.query(models.MemoryArtifact).filter(
        models.MemoryArtifact.case_id == case_id,
        models.MemoryArtifact.suspicious == True
    ).all()
    network = db.query(models.NetworkArtifact).filter(
        models.NetworkArtifact.case_id == case_id,
        models.NetworkArtifact.flagged == True
    ).all()
    registry = db.query(models.RegistryKey).filter(
        models.RegistryKey.case_id == case_id,
        models.RegistryKey.flagged == True
    ).all()
    malware = db.query(models.MalwareSample).filter(models.MalwareSample.case_id == case_id).all()

    return {
        "case_name": case.name,
        "case_id": case_id,
        "investigator": case.investigator,
        "status": case.status,
        "priority": case.priority,
        "incident_type": case.incident_type,
        "evidence_count": len(evidence),
        "artifact_count": len(artifacts),
        "flagged_artifact_count": len(flagged),
        "flagged_artifacts": [{"name": a.name, "reason": a.flagged_reason, "type": a.artifact_type} for a in flagged[:10]],
        "yara_matches": len(yara),
        "sigma_alerts": [{"title": a.title, "severity": a.severity, "technique": a.mitre_technique} for a in sigma],
        "ioc_hits": len(ioc_matches),
        "suspicious_processes": [{"pid": p.pid, "name": p.name, "cmd": p.command_line} for p in memory[:5]],
        "network_flags": [{"dst": n.dst_ip, "host": n.hostname, "reason": n.flag_reason} for n in network[:5]],
        "registry_flags": [{"path": r.key_path, "name": r.value_name, "reason": r.flag_reason} for r in registry[:5]],
        "malware_samples": [{"filename": m.filename, "risk": m.risk_score, "packed": m.is_packed} for m in malware[:5]],
    }


def _generate_ai_response(user_message: str, context: dict) -> tuple[str, list]:
    """Generate a contextual AI response based on case data using Google Gemini AI REST API."""
    import os
    import json
    import requests
    from dotenv import load_dotenv

    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "your_gemini_api_key_here":
        # Fallback if no API key is provided
        return (
            "⚠️ **Gemini API Key is missing or invalid.**\n\n"
            "Please configure your `GEMINI_API_KEY` in the `backend/.env` file to enable the AI Investigation Assistant.\n\n"
            f"**Case Context Loaded:**\n"
            f"- **{context.get('case_name')}** ({context.get('incident_type', 'Unknown')} Incident)\n"
            f"- {context.get('evidence_count', 0)} Evidence Items\n"
            f"- {context.get('artifact_count', 0)} Extracted Artifacts\n"
            f"- {context.get('flagged_artifact_count', 0)} Flagged Anomalies",
            []
        )

    # Build the system prompt with RAG context
    system_prompt = f"""You are an elite Digital Forensics and Incident Response (DFIR) AI assistant.
You are helping an investigator analyze a case in the DFIOP (Digital Forensics Investigation Operating Platform).
Base your analysis ONLY on the provided case context below. Be highly analytical, precise, and professional.

CASE CONTEXT:
=========================================
Case Name: {context.get('case_name')}
Investigator: {context.get('investigator')}
Status: {context.get('status')} | Priority: {context.get('priority')} | Type: {context.get('incident_type')}

Evidence Items: {context.get('evidence_count', 0)}
Total Artifacts: {context.get('artifact_count', 0)}
Flagged Artifacts: {context.get('flagged_artifact_count', 0)}
YARA Matches: {context.get('yara_matches', 0)}
Sigma Alerts: {len(context.get('sigma_alerts', []))}
IOC Hits: {context.get('ioc_hits', 0)}

FLAGGED ARTIFACTS:
{json.dumps(context.get('flagged_artifacts', []), indent=2)}

SIGMA ALERTS:
{json.dumps(context.get('sigma_alerts', []), indent=2)}

SUSPICIOUS MEMORY PROCESSES:
{json.dumps(context.get('suspicious_processes', []), indent=2)}

SUSPICIOUS NETWORK ACTIVITY:
{json.dumps(context.get('network_flags', []), indent=2)}

MALWARE SAMPLES:
{json.dumps(context.get('malware_samples', []), indent=2)}
=========================================

Answer the investigator's query based on the above context. If the query asks for something not in the context, state that you don't have that information.
Format your response using Markdown. Be concise but thorough."""

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": system_prompt + "\n\nUser Query: " + user_message}]
                }
            ]
        }
        
        resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        
        if not resp.ok:
            if resp.status_code in (400, 401, 403, 404):
                # Fallback to local simulation if the API key is invalid/unauthorized
                return _simulate_ai_response(user_message, context)
            
            error_msg = resp.text
            try:
                err_json = resp.json()
                if "error" in err_json:
                    error_msg = err_json["error"].get("message", resp.text)
            except:
                pass
            return f"❌ **Gemini API Error ({resp.status_code}):**\n\n`{error_msg}`", []

        data = resp.json()
        response_text = data["candidates"][0]["content"]["parts"][0]["text"]

        citations = []
        if context.get("flagged_artifact_count", 0) > 0:
            citations.append({"type": "artifacts", "ref": "flagged", "label": f"{context.get('flagged_artifact_count')} Flagged Artifacts"})
        if context.get("sigma_alerts"):
            citations.append({"type": "detections", "ref": "sigma", "label": "Sigma Detections"})
        
        return response_text, citations

    except Exception as e:
        return f"❌ **Error communicating with Gemini AI REST API:**\n\n`{str(e)}`", []

def _simulate_ai_response(user_message: str, context: dict) -> tuple[str, list]:
    """Fallback simulated response if the provided API key is a dummy or unauthorized key."""
    msg = user_message.lower()
    citations = []

    if any(w in msg for w in ["summarize", "summary", "overview", "what happened"]):
        resp = f"## Case Summary: {context.get('case_name', 'Unknown')}\n\n"
        resp += f"This is a **{context.get('priority', 'medium')} priority** {context.get('incident_type', 'investigation')} case with **{context.get('evidence_count', 0)} evidence items** and **{context.get('artifact_count', 0)} artifacts**.\n\n"
        if context.get('flagged_artifact_count', 0) > 0:
            resp += f"**{context['flagged_artifact_count']} artifacts** were flagged by anomaly detection.\n"
        if context.get('sigma_alerts'):
            resp += f"\n### Sigma Detections ({len(context['sigma_alerts'])} alerts):\n"
            for a in context['sigma_alerts'][:3]:
                resp += f"- **[{a['severity'].upper()}]** {a['title']} — `{a['technique']}`\n"
        if context.get('suspicious_processes'):
            resp += f"\n### Suspicious Processes:\n"
            for p in context['suspicious_processes'][:3]:
                resp += f"- PID {p['pid']} `{p['name']}` → {p['cmd'][:60]}...\n"
        citations = [{"type": "case", "ref": context.get('case_id'), "label": context.get('case_name')}]

    elif any(w in msg for w in ["malware", "executable", "packed", "suspicious file"]):
        samples = context.get('malware_samples', [])
        if samples:
            resp = f"## Malware Analysis Results\n\nFound **{len(samples)} potential malware sample(s)**:\n\n"
            for s in samples:
                resp += f"- **{s['filename']}** → Risk Score: {s['risk']:.0f}/100"
                if s['packed']:
                    resp += " 📦 Packed"
                resp += "\n"
            resp += "\nRecommendation: Submit samples to VirusTotal and run YARA rules for signature matching."
        else:
            resp = "No malware samples have been analyzed yet. Run **Malware Analysis** first from the Malware page."
        citations = [{"type": "malware", "ref": "malware-analysis", "label": "Malware Analysis Module"}]

    elif any(w in msg for w in ["network", "connection", "c2", "command and control", "ip", "domain"]):
        flags = context.get('network_flags', [])
        if flags:
            resp = f"## Suspicious Network Activity\n\n{len(flags)} flagged connections:\n\n"
            for n in flags:
                resp += f"- **{n['dst']}** ({n['host'] or 'no hostname'}) → {n['reason']}\n"
            resp += "\n**Recommendation:** Block these destinations at the firewall and check for similar connections from other endpoints."
        else:
            resp = "No suspicious network connections detected. Run **Network Analysis** to parse PCAP data."
        citations = [{"type": "network", "ref": "network-forensics", "label": "Network Forensics Module"}]

    elif any(w in msg for w in ["report", "executive", "brief", "findings"]):
        resp = f"## Executive Summary — {context.get('case_name')}\n\n"
        resp += f"**Incident Type:** {context.get('incident_type', 'Unknown')}\n"
        resp += f"**Priority:** {context.get('priority', 'Medium')}\n"
        resp += f"**Status:** {context.get('status', 'open')}\n\n"
        resp += "### Key Findings\n"
        resp += f"- {context.get('evidence_count', 0)} evidence items acquired and verified\n"
        resp += f"- {context.get('flagged_artifact_count', 0)} anomalous artifacts detected\n"
        if context.get('sigma_alerts'):
            resp += f"- {len(context['sigma_alerts'])} Sigma detections covering MITRE ATT&CK techniques\n"
        if context.get('suspicious_processes'):
            resp += f"- {len(context['suspicious_processes'])} suspicious processes identified in memory\n"
        if context.get('network_flags'):
            resp += f"- {len(context['network_flags'])} suspicious network connections including possible C2\n"
        resp += "\n### Recommendations\n"
        resp += "1. Isolate affected endpoints immediately\n"
        resp += "2. Revoke all credentials used on affected systems\n"
        resp += "3. Block identified C2 domains and IPs at perimeter\n"
        resp += "4. Preserve all evidence under chain-of-custody for legal proceedings\n"
        citations = [{"type": "report", "ref": "executive-summary", "label": "Auto-generated from case data"}]

    elif any(w in msg for w in ["ioc", "indicator", "hash", "domain"]):
        hits = context.get('ioc_hits', 0)
        resp = f"## IOC Analysis\n\n**{hits} IOC matches** found in this case.\n\n"
        if context.get('network_flags'):
            resp += "### Network IOCs:\n"
            for n in context['network_flags']:
                if n['host']:
                    resp += f"- Domain: `{n['host']}` → {n['reason']}\n"
                resp += f"- IP: `{n['dst']}` → {n['reason']}\n"
        resp += "\n**Recommendation:** Cross-reference with MISP and VirusTotal for threat intelligence enrichment."
        citations = [{"type": "ioc", "ref": "ioc-hunting", "label": "IOC Hunting Module"}]

    elif any(w in msg for w in ["next steps", "recommend", "what should", "action"]):
        resp = "## Recommended Next Steps\n\n"
        if context.get('flagged_artifact_count', 0) > 0:
            resp += f"1. **Review {context['flagged_artifact_count']} flagged artifacts** in the Evidence Explorer for analyst verification\n"
        if context.get('sigma_alerts'):
            resp += "2. **Acknowledge Sigma alerts** and map them to your incident response playbook\n"
        resp += "3. **Run YARA scan** against all evidence files to check for known malware signatures\n"
        resp += "4. **Analyze memory dump** with Volatility3 to find injected code and hidden processes\n"
        resp += "5. **Generate a full PDF report** for documentation and chain-of-custody purposes\n"
        resp += "6. **Cross-reference IOCs** with external threat intelligence (MISP, VirusTotal)\n"
        resp += "7. **Update MITRE ATT&CK mapping** based on confirmed techniques\n"
        citations = [{"type": "guidance", "ref": "ai-assistant", "label": "Investigation Guidance"}]

    else:
        resp = f"*(Simulated Response Mode)*\n\nI'm analyzing case **{context.get('case_name', 'Unknown')}** which has {context.get('artifact_count', 0)} artifacts and {context.get('evidence_count', 0)} evidence items.\n\n"
        resp += "I can help you:\n- **Summarize** the investigation findings\n- **Analyze malware** samples\n- **Review network** connections and C2 indicators\n- **Generate IOC lists** for threat hunting\n- **Create executive reports** for stakeholders\n- **Recommend next steps** in the investigation\n\nWhat would you like to know?"
        citations = []

    return resp, citations


@router.post("/cases/{case_id}/ai/chat")
def chat(case_id: str, payload: schemas.AIMessageRequest, db: Session = Depends(get_db)):
    case = db.get(models.Case, case_id)
    if not case:
        raise HTTPException(404, "Case not found")

    context = _build_case_context(db, case_id)
    response_text, citations = _generate_ai_response(payload.message, context)
    now = dt.datetime.utcnow()

    # Load or create session
    session_id = payload.session_id
    if session_id:
        session = db.get(models.AISession, session_id)
    else:
        session = None

    if not session:
        session = models.AISession(case_id=case_id, messages_json="[]")
        db.add(session)
        db.flush()

    messages = json.loads(session.messages_json or "[]")
    messages.append({"role": "user", "content": payload.message, "citations": [], "ts": now.isoformat()})
    messages.append({"role": "assistant", "content": response_text, "citations": citations, "ts": now.isoformat()})
    session.messages_json = json.dumps(messages)
    session.updated_at = now
    db.commit()
    db.refresh(session)

    log_action(db, case_id, "ai_query", f"Query: {payload.message[:80]}")

    return {
        "session_id": session.id,
        "role": "assistant",
        "content": response_text,
        "citations": citations,
        "timestamp": now.isoformat(),
    }


@router.get("/cases/{case_id}/ai/sessions/{session_id}")
def get_session(case_id: str, session_id: str, db: Session = Depends(get_db)):
    session = db.get(models.AISession, session_id)
    if not session or session.case_id != case_id:
        raise HTTPException(404, "Session not found")
    return {"session_id": session.id, "messages": json.loads(session.messages_json)}
