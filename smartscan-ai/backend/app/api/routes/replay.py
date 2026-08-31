from fastapi import APIRouter

router = APIRouter()

@router.post("/play")
def replay_dataset():
    return {"status": "playing"}
