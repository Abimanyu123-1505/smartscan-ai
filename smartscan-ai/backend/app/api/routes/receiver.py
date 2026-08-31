from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def get_receiver_status():
    return {"tuning_freq": 100.0}
