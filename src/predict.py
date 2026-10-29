import joblib
import pandas as pd

from src.config import MODEL_PATH


class HousingPredictor:

    def __init__(self):
        bundle = joblib.load(MODEL_PATH)

        self.model = bundle["model"]
        self.features = bundle["features"]

    def predict(self, features: dict) -> float:
        input_data = pd.DataFrame(
            [features],
            columns=self.features,
        )

        prediction = self.model.predict(input_data)[0]

        return float(prediction)