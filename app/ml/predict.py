
from pathlib import Path

import joblib
import pandas as pd

from app.core.database import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT / "app" / "ml" / "models" / "demand_model.joblib"
)

MIN_HISTORY_DAYS = 30
HISTORY_WINDOW_DAYS = 30


def get_product_info(product_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, category
                FROM products
                WHERE product_id = %s;
            """, (product_id,))

            return cur.fetchone()


def get_sales_history(product_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    sold_at::date AS sale_date,
                    SUM(quantity) AS units_sold
                FROM sales
                WHERE product_id = %s
                  AND sold_at >= CURRENT_DATE - INTERVAL '29 days'
                GROUP BY sold_at::date
                ORDER BY sale_date;
            """, (product_id,))

            rows = cur.fetchall()

    history = pd.DataFrame(
        rows,
        columns=["date", "units_sold"]
    )

    if not history.empty:
        history["date"] = pd.to_datetime(history["date"])

    return history


def get_category_demand(category, product_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(DISTINCT p.product_id),
                    COALESCE(SUM(s.quantity), 0)
                FROM products p
                LEFT JOIN sales s
                    ON p.product_id = s.product_id
                    AND s.sold_at >= CURRENT_DATE - INTERVAL '29 days'
                WHERE p.category IS NOT DISTINCT FROM %s
                  AND p.product_id != %s;
            """, (category, product_id))

            peer_count, total_units = cur.fetchone()

    if peer_count > 0 and total_units > 0:
        return total_units / (peer_count * HISTORY_WINDOW_DAYS), "category_average"

    return None, None


def get_store_demand(product_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(DISTINCT p.product_id),
                    COALESCE(SUM(s.quantity), 0)
                FROM products p
                LEFT JOIN sales s
                    ON p.product_id = s.product_id
                    AND s.sold_at >= CURRENT_DATE - INTERVAL '29 days'
                WHERE p.product_id != %s;
            """, (product_id,))

            product_count, total_units = cur.fetchone()

    if product_count > 0 and total_units > 0:
        return total_units / (product_count * HISTORY_WINDOW_DAYS), "store_average"

    return 0.0, "no_store_sales"


def predict_product_demand(product_id):

    product = get_product_info(product_id)

    if product is None:
        raise ValueError("Product not found")

    product_name, category = product

    history = get_sales_history(product_id)

    today = pd.Timestamp.today().normalize()
    next_date = today + pd.Timedelta(days=1)

    # Create a complete 30-day calendar history.
    date_range = pd.date_range(
        end=today,
        periods=HISTORY_WINDOW_DAYS,
        freq="D"
    )

    if not history.empty:
        history = (
            history.set_index("date")
            .reindex(date_range, fill_value=0)
            .rename_axis("date")
            .reset_index()
        )
    else:
        history = pd.DataFrame({
            "date": date_range,
            "units_sold": 0
        })

    # Use the ML model only when sufficient history exists.
    if not history.empty and history["units_sold"].sum() > 0:
        # A full 30-day window is available, including zero-sale days.
        if history["units_sold"].sum() > 0 and not history["date"].empty:
            first_sale_date = (
                get_sales_history(product_id)["date"].min()
            )
            history_days = (today - first_sale_date).days + 1
        else:
            history_days = 0
    else:
        history_days = 0

    if history_days >= MIN_HISTORY_DAYS:
        if not MODEL_PATH.exists():
            raise FileNotFoundError("Trained model not found")

        model = joblib.load(MODEL_PATH)

        recent_sales = history["units_sold"]

        input_data = pd.DataFrame([{
            "product_id": str(product_id),
            "day_of_week": next_date.dayofweek,
            "month": next_date.month,
            "lag_1": recent_sales.iloc[-1],
            "rolling_mean_7": recent_sales.tail(7).mean(),
            "rolling_mean_30": recent_sales.tail(30).mean()
        }])

        prediction = float(model.predict(input_data)[0])
        forecast_source = "ml_model"

    else:
        # Estimate demand using category or store-level data.
        baseline, forecast_source = get_category_demand(
            category, product_id
        )

        if baseline is None:
            baseline, forecast_source = get_store_demand(product_id)

        # Blend the baseline with the product's own limited sales.
        own_daily_demand = history["units_sold"].sum() / HISTORY_WINDOW_DAYS

        if history["units_sold"].sum() > 0:
            prediction = (
                0.7 * baseline + 0.3 * own_daily_demand
            )
        else:
            prediction = baseline

    return {
        "product_id": product_id,
        "product_name": product_name,
        "prediction_date": str(next_date.date()),
        "predicted_daily_demand": round(max(0, prediction), 2),
        "forecast_source": forecast_source,
        "history_days": history_days
    }
