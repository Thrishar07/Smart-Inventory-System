import pandas as pd


def create_features(df):

    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])

    df = df.sort_values(
        ["product_id", "date"]
    )

    # Calendar features
    df["day_of_week"] = df["date"].dt.day_of_week
    df["month"] = df["date"].dt.month

    # Previous sales
    df["lag_1"] = (
        df.groupby("product_id")["units_sold"]
        .shift(1)
    )

    # Previous 7-day average
    df["rolling_mean_7"] = (
        df.groupby("product_id")["units_sold"]
        .transform(
            lambda x: x.shift(1).rolling(7).mean()
        )
    )

    # Previous 30-day average
    df["rolling_mean_30"] = (
        df.groupby("product_id")["units_sold"]
        .transform(
            lambda x: x.shift(1).rolling(30).mean()
        )
    )

    df = df.dropna()

    return df


if __name__ == "__main__":

    df = pd.read_csv("data/daily_sales.csv")

    featured_df = create_features(df)

    featured_df.to_csv(
        "data/ml_features.csv",
        index=False
    )

    print("Feature engineering completed!")
    print(featured_df.head())
    print("Total rows:", len(featured_df))