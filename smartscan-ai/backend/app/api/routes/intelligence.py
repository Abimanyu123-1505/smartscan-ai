from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def get_intel_status():
    return {"learning": True}
