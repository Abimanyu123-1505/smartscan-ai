from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import asyncio

router = APIRouter(prefix="/api/replay")

class ReplaySessionState:
    def __init__(self, session_id: str, policy_name: str):
        self.session_id = session_id
        self.policy_name = policy_name
        self.current_slot = 0
        self.receiver = None
        self.engine = None
        self.belief = None
        self.evaluator = None
        self.events = []
        
sessions: Dict[str, ReplaySessionState] = {}

class InitRequest(BaseModel):
    recording_id: str
    policy: str
    n_freq_bins: Optional[int] = None
    seed: Optional[int] = None

@router.post("/init")
def init_session(req: InitRequest):
    session_id = str(uuid.uuid4())
    state = ReplaySessionState(session_id, req.policy)
    # Mocking initialization for API skeleton
    sessions[session_id] = state
    return {
        "session_id": session_id,
        "num_slots": 1000,
        "num_freq_bins": req.n_freq_bins or 256,
        "freq_bins_hz": [i * 1000 for i in range(req.n_freq_bins or 256)]
    }

@router.post("/{session_id}/step")
def step_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = sessions[session_id]
    state.current_slot += 1
    
    return {
        "slot": state.current_slot,
        "freq_bin": 0,
        "freq_hz": 0.0,
        "power_db": -100.0,
        "detected": False,
        "switched": False,
        "belief_snapshot": {},
        "decision_explanation": "mock step"
    }

@router.get("/{session_id}/state")
def get_state(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    state = sessions[session_id]
    return {"session_id": state.session_id, "current_slot": state.current_slot}

@router.get("/{session_id}/metrics")
def get_metrics(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "mock_metrics"}

@router.delete("/{session_id}")
def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "deleted"}

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    if session_id not in sessions:
        await websocket.close(code=1008)
        return
        
    try:
        while True:
            # Mock streaming
            await asyncio.sleep(0.1) # ~10Hz
            state = sessions.get(session_id)
            if not state:
                break
            state.current_slot += 1
            await websocket.send_json({
                "slot": state.current_slot,
                "freq_bin": 0,
                "freq_hz": 0.0,
                "power_db": -100.0,
                "detected": False,
                "switched": False,
                "belief_snapshot": {},
                "decision_explanation": "mock step stream"
            })
    except WebSocketDisconnect:
        pass
