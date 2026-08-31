from fastapi import APIRouter

router = APIRouter()

@router.get("/current")
def get_current_policy():
    return {"policy": "smartscan"}
