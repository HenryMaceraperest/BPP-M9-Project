from sklearn.datasets import fetch_california_housing

from src.config import DATA_PATH


def main():
    print("Fetching California Housing dataset...")

    housing = fetch_california_housing(as_frame=True)

    df = housing.frame

    DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        DATA_PATH,
        index=False,
    )

    print(f"Saved {len(df)} rows to {DATA_PATH}")


if __name__ == "__main__":
    main()