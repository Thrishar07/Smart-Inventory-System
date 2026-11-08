import math

from fastapi import APIRouter, HTTPException

from app.core.database import get_connection
from app.ml.predict import predict_product_demand

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/reorder/{product_id}")
def get_reorder_recommendation(product_id: int):

    try:
        # Fetch current inventory and supplier information
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        p.name,
                        i.quantity_on_hand,
                        i.safety_stock,
                        s.lead_time_days
                    FROM products p
                    JOIN inventory i
                        ON p.product_id = i.product_id
                    LEFT JOIN suppliers s
                        ON p.supplier_id = s.supplier_id
                    WHERE p.product_id = %s;
                """, (product_id,))

                row = cur.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Product or inventory record not found"
            )

        product_name = row[0]
        current_stock = row[1]
        safety_stock = row[2]
        lead_time = row[3]

        if lead_time is None:
            raise HTTPException(
                status_code=422,
                detail="Supplier lead time is not configured"
            )

        # Get predicted demand from our ML model
        prediction = predict_product_demand(product_id)

        daily_demand = prediction["predicted_daily_demand"]

        # Calculate reorder point
        reorder_point = (
            daily_demand * lead_time
        ) + safety_stock

        # Calculate estimated days remaining
        if daily_demand > 0:
            days_remaining = current_stock / daily_demand
        else:
            days_remaining = None

        # Determine stock risk
        if days_remaining is None:
            risk = "UNKNOWN"
        elif days_remaining <= lead_time:
            risk = "CRITICAL"
        elif days_remaining <= lead_time + 2:
            risk = "HIGH"
        else:
            risk = "LOW"

        reorder_recommended = current_stock <= reorder_point

        return {
            "product_id": product_id,
            "product_name": product_name,
            "current_stock": current_stock,
            
            "predicted_daily_demand": daily_demand,
            "forecast_source": prediction["forecast_source"],
            "history_days": prediction["history_days"],
            "estimated_days_remaining": (
                round(days_remaining, 2)
                if days_remaining is not None else None
            ),
            "supplier_lead_time_days": lead_time,
            "safety_stock": safety_stock,
            "reorder_point": round(reorder_point, 2),
            "reorder_recommended": reorder_recommended,
            "stock_risk": risk,
            "minimum_stock_shortfall": max(
                0, math.ceil(reorder_point - current_stock)
            )
        }

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Trained ML model not found"
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not generate reorder recommendation"
        )