from fastapi import APIRouter

router = APIRouter()

@router.post("/predict")
def predict_next():
    return {"prediction": 0}
