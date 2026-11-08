from fastapi import APIRouter, HTTPException
from app.core.database import get_connection

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/stockout-risk")
def get_stockout_risk():

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute("""
                    SELECT
                        p.product_id,
                        p.name,
                        i.quantity_on_hand,
                        i.safety_stock,
                        s.lead_time_days,
                        COALESCE(SUM(sa.quantity), 0) AS units_sold
                    FROM products p
                    JOIN inventory i
                        ON p.product_id = i.product_id
                    LEFT JOIN suppliers s
                        ON p.supplier_id = s.supplier_id
                    LEFT JOIN sales sa
                        ON p.product_id = sa.product_id
                        AND sa.sold_at >=
                            CURRENT_TIMESTAMP - INTERVAL '7 days'
                    GROUP BY
                        p.product_id,
                        p.name,
                        i.quantity_on_hand,
                        i.safety_stock,
                        s.lead_time_days
                    ORDER BY p.product_id;
                """)

                rows = cur.fetchall()

        results = []

        for row in rows:
            product_id = row[0]
            name = row[1]
            current_stock = row[2]
            safety_stock = row[3]
            lead_time = row[4] if row[4] is not None else 0
            units_sold = row[5]

            # Average demand per day over 7 calendar days
            avg_daily_demand = units_sold / 7

            # Estimate how many days the stock will last
            if avg_daily_demand > 0:
                days_remaining = current_stock / avg_daily_demand
            else:
                days_remaining = None

            # Calculate reorder point
            reorder_point = (
                avg_daily_demand * lead_time
            ) + safety_stock

            # Determine stockout risk
            if avg_daily_demand == 0:
                risk = "UNKNOWN"
            elif days_remaining <= 2:
                risk = "CRITICAL"
            elif days_remaining <= 5:
                risk = "HIGH"
            else:
                risk = "LOW"

            results.append({
                "product_id": product_id,
                "product_name": name,
                "current_stock": current_stock,
                "units_sold_last_7_days": units_sold,
                "average_daily_demand": round(avg_daily_demand, 2),
                "estimated_days_remaining": (
                    round(days_remaining, 2)
                    if days_remaining is not None else None
                ),
                "lead_time_days": lead_time,
                "safety_stock": safety_stock,
                "reorder_point": round(reorder_point, 2),
                "reorder_recommended": (
                    current_stock <= reorder_point
                ),
                "risk_level": risk
            })

        return results

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not calculate stockout risk"
        )