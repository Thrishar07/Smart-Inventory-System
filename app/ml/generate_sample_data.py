import numpy as np
import pandas as pd
from pathlib import Path


def generate_sales_data():

    np.random.seed(42)

    products = {
        1: {"name": "Rice 5kg", "daily_demand": 8},
        2: {"name": "Cooking Oil 1L", "daily_demand": 6},
        3: {"name": "Milk 1L", "daily_demand": 15},
        4: {"name": "Bread", "daily_demand": 12},
        5: {"name": "Shampoo 200ml", "daily_demand": 3},
        9: {"name": "Notebook", "daily_demand": 5}
    }

    dates = pd.date_range(
        end=pd.Timestamp.today().normalize(),
        periods=180,
        freq="D"
    )

    records = []

    for product_id, details in products.items():

        base_demand = details["daily_demand"]

        for date in dates:

            # Weekend demand is slightly higher
            weekend_factor = (
                1.3 if date.dayofweek >= 5 else 1.0
            )

            # Random daily variation
            random_factor = np.random.uniform(0.7, 1.3)

            # Calculate expected daily demand
            expected_demand = (
                base_demand
                * weekend_factor
                * random_factor
            )

            # Generate realistic integer sales
            units_sold = np.random.poisson(expected_demand)

            records.append({
                "product_id": product_id,
                "product_name": details["name"],
                "date": date,
                "units_sold": units_sold
            })

    df = pd.DataFrame(records)

    project_root = Path(__file__).resolve().parents[2]

    output_file = (
        project_root / "data" / "synthetic_daily_sales.csv"
    )

    df.to_csv(output_file, index=False)

    print("Synthetic sales dataset generated!")
    print("Total records:", len(df))
    print("Total products:", df["product_id"].nunique())
    print("Date range:", df["date"].min(), "to", df["date"].max())
    print("Total units sold:", df["units_sold"].sum())
    print("Saved to:", output_file)

    return df


if __name__ == "__main__":
    generate_sales_data()