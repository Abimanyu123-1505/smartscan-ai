from fastapi import APIRouter

router = APIRouter()

@router.post("/run")
def run_experiment():
    return {"job_id": "123"}
