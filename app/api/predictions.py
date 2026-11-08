from fastapi import APIRouter, HTTPException

from app.ml.predict import predict_product_demand

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"]
)


@router.get("/demand/{product_id}")
def predict_demand(product_id: int):

    try:
        return predict_product_demand(product_id)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not predict product demand"
        )