from sklearn.datasets import fetch_california_housing

from src.config import DATA_PATH


def main():
    if DATA_PATH.exists():
        raise FileExistsError(
            f"{DATA_PATH} already exists. "
            "Delete it explicitly if you intend to replace "
            "the versioned dataset."
        )
    
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
    print("This file must now be added to DVC.")


if __name__ == "__main__":
    main()