from pathlib import Path

import pandas as pd

from app.core.database import get_connection


def prepare_daily_sales():
    # Fetch daily sales for every product over the last 90 days
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    p.product_id,
                    d.sale_date::date AS sale_date,
                    COALESCE(SUM(s.quantity), 0)::INTEGER AS units_sold
                FROM products p
                CROSS JOIN generate_series(
                    CURRENT_DATE - INTERVAL '89 days',
                    CURRENT_DATE,
                    INTERVAL '1 day'
                ) AS d(sale_date)
                LEFT JOIN sales s
                    ON s.product_id = p.product_id
                    AND s.sold_at >= d.sale_date
                    AND s.sold_at < d.sale_date + INTERVAL '1 day'
                GROUP BY p.product_id, d.sale_date
                ORDER BY p.product_id, d.sale_date;
            """)

            rows = cur.fetchall()

    # Convert database records into a Pandas DataFrame
    df = pd.DataFrame(
        rows,
        columns=["product_id", "date", "units_sold"]
    )

    # Save the dataset inside the project's data directory
    project_root = Path(__file__).resolve().parents[2]
    output_file = project_root / "data" / "daily_sales.csv"

    df.to_csv(output_file, index=False)

    print("Daily sales dataset created successfully!")
    print(f"Total records: {len(df)}")
    print(f"Total products: {df['product_id'].nunique()}")
    print(f"Saved to: {output_file}")

    return df


if __name__ == "__main__":
    prepare_daily_sales()