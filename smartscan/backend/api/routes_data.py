from fastapi import APIRouter, HTTPException
from pathlib import Path
import yaml
import json
from typing import List, Dict, Any

router = APIRouter(prefix="/api")

# Assuming root is where main.py runs
DATA_DIR = Path(__file__).parent.parent.parent / 'data'

@router.get("/health")
def health_check():
    return {
        'status': 'ok',
        'service': 'SmartScan AI',
        'version': '1.0.0-milestone1',
        'mode': 'real_data'
    }

@router.get("/datasets")
def list_datasets() -> List[Dict[str, Any]]:
    datasets_file = DATA_DIR / 'datasets.yaml'
    if not datasets_file.exists():
        return []
    with open(datasets_file, 'r') as f:
        data = yaml.safe_load(f)
        return data.get('datasets', [])

@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str):
    datasets = list_datasets()
    for ds in datasets:
        if ds.get('dataset_id') == dataset_id:
            return ds
    raise HTTPException(status_code=404, detail="Dataset not found")

@router.get("/recordings")
def list_recordings():
    raw_dir = DATA_DIR / 'raw'
    if not raw_dir.exists():
        return []
        
    recordings = []
    for p in raw_dir.glob('**/*'):
        if p.is_file() and (p.suffix == '.sigmf-meta' or p.suffix == '.json'):
            recordings.append({
                "recording_id": p.stem,
                "filename": p.name,
                "path": str(p.relative_to(DATA_DIR))
            })
    return recordings

@router.get("/recordings/{recording_id}/metadata")
def get_recording_metadata(recording_id: str):
    # Dummy mock for now, actual implementation would load via SigMFReader
    return {"recording_id": recording_id, "status": "mock_metadata"}

@router.get("/recordings/{recording_id}/psd")
def get_recording_psd(recording_id: str):
    # Dummy mock for now
    return {"recording_id": recording_id, "status": "mock_psd"}

@router.get("/recordings/{recording_id}/events")
def get_recording_events(recording_id: str):
    # Dummy mock for now
    return {"recording_id": recording_id, "events": []}
