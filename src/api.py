from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from src.predict import HousingPredictor


predictor = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    global predictor

    predictor = HousingPredictor()

    yield

    predictor = None


app = FastAPI(
    title="California Housing Valuation API",
    description=(
        "Example regression API using the "
        "California Housing dataset."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


class HousingFeatures(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float


class PredictionResponse(BaseModel):

    predicted_value: float
    predicted_value_usd: float
    warning: str


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": predictor is not None,
    }


@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(features: HousingFeatures):

    prediction = predictor.predict(
        features.model_dump()
    )

    return PredictionResponse(
        predicted_value=round(
            prediction,
            4,
        ),
        predicted_value_usd=round(
            prediction * 100_000,
            2,
        ),
        warning=(
            "This model uses historical 1990 census data "
            "and predicts census block-group median house "
            "value. The target is capped and should not be "
            "interpreted as a current individual property valuation."
        ),
    )