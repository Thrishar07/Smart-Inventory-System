from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


from app.ml.features import create_features


def train_model():

    # Load synthetic sales data
    project_root = Path(__file__).resolve().parents[2]

    data_file = project_root / "data" / "synthetic_daily_sales.csv"

    df = pd.read_csv(data_file)

    # Generate historical demand features
    df = create_features(df)

    # Treat product ID as a category, not a numerical quantity
    df["product_id"] = df["product_id"].astype(str)

    feature_columns = [
        "product_id",
        "day_of_week",
        "month",
        "lag_1",
        "rolling_mean_7",
        "rolling_mean_30"
    ]

    X = df[feature_columns]
    y = df["units_sold"]

    # Split chronologically: earlier dates for training,
    # latest 20% of dates for testing
    unique_dates = sorted(df["date"].unique())
    split_index = int(len(unique_dates) * 0.8)
    cutoff_date = unique_dates[split_index]

    train_mask = df["date"] < cutoff_date
    test_mask = df["date"] >= cutoff_date

    X_train = X.loc[train_mask]
    X_test = X.loc[test_mask]

    y_train = y.loc[train_mask]
    y_test = y.loc[test_mask]

    # Convert product IDs into one-hot encoded features
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "product",
                OneHotEncoder(handle_unknown="ignore"),
                ["product_id"]
            )
        ],
        remainder="passthrough"
    )

    # Build the Random Forest pipeline
    model = Pipeline([
        ("preprocessor", preprocessor),
        (
            "regressor",
            RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                min_samples_leaf=2
            )
        )
    ])

    # Train the model
    model.fit(X_train, y_train)

    # Evaluate on unseen future dates
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5

    print("\nModel training completed!")
    print("Training records:", len(X_train))
    print("Testing records:", len(X_test))
    print("Test starts from:", cutoff_date)

    print("\nModel Evaluation:")
    print("MAE:", round(mae, 2))
    print("RMSE:", round(rmse, 2))

    # Save trained model
    model_dir = project_root / "app" / "ml" / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "demand_model.joblib"

    joblib.dump(model, model_path)

    print("\nModel saved to:", model_path)


if __name__ == "__main__":
    train_model()