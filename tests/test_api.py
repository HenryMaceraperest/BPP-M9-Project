from fastapi.testclient import TestClient

from src.api import app


example = {
    "MedInc": 8.3252,
    "HouseAge": 41.0,
    "AveRooms": 6.984127,
    "AveBedrms": 1.023810,
    "Population": 322.0,
    "AveOccup": 2.555556,
    "Latitude": 37.88,
    "Longitude": -122.23,
}


def test_health():

    with TestClient(app) as client:

        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_prediction():

    with TestClient(app) as client:

        response = client.post(
            "/predict",
            json=example,
        )

        assert response.status_code == 200

        result = response.json()

        assert result["predicted_value"] > 0
        assert result["predicted_value_usd"] > 0


def test_missing_feature():

    invalid_example = example.copy()

    del invalid_example["MedInc"]

    with TestClient(app) as client:

        response = client.post(
            "/predict",
            json=invalid_example,
        )

        assert response.status_code == 422