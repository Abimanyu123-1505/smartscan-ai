from fastapi import APIRouter

router = APIRouter()

@router.post("/start")
def start_simulation():
    return {"status": "started"}
