import json

import joblib
import pandas as pd
import yaml

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split

from src.config import (
    DATA_PATH,
    FEATURES,
    METRICS_PATH,
    MODEL_PATH,
    PARAMS_PATH,
    TARGET,
)


def load_params():
    with open(PARAMS_PATH, "r") as file:
        return yaml.safe_load(file)


def main():
    params = load_params()

    print("Loading dataset...")

    df = pd.read_parquet(DATA_PATH)

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=params["data"]["test_size"],
        random_state=params["data"]["random_state"],
    )

    print("Training model...")

    model = RandomForestRegressor(
        n_estimators=params["model"]["n_estimators"],
        max_depth=params["model"]["max_depth"],
        min_samples_leaf=params["model"]["min_samples_leaf"],
        random_state=params["data"]["random_state"],
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    metrics = {
        "mae": mean_absolute_error(
            y_test,
            predictions,
        ),
        "rmse": mean_squared_error(
            y_test,
            predictions,
        ) ** 0.5,
        "r2": r2_score(
            y_test,
            predictions,
        ),
    }

    metrics = {
        name: float(value)
        for name, value in metrics.items()
    }

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    METRICS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model_bundle = {
        "model": model,
        "features": FEATURES,
    }

    joblib.dump(
        model_bundle,
        MODEL_PATH,
    )

    with open(METRICS_PATH, "w") as file:
        json.dump(
            metrics,
            file,
            indent=4,
        )

    print("Training complete.")
    print(json.dumps(metrics, indent=4))


if __name__ == "__main__":
    main()