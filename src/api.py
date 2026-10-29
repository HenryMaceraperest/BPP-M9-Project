from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.predict import HousingPredictor
import logging

logger = logging.getLogger(__name__)

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
        json_schema_extra={
            "example": {
                "MedInc": 8.3252,
                "HouseAge": 41.0,
                "AveRooms": 6.984127,
                "AveBedrms": 1.023810,
                "Population": 322.0,
                "AveOccup": 2.555556,
                "Latitude": 37.88,
                "Longitude": -122.23,
            }
        },
    )

    MedInc: float = Field(
        gt=0,
        le=20,
        description=(
            "Median income in tens of thousands of US dollars."
        ),
    )

    HouseAge: float = Field(
        ge=0,
        le=100,
        description="Median house age in years.",
    )

    AveRooms: float = Field(
        gt=0,
        le=200,
        description="Average rooms per household.",
    )

    AveBedrms: float = Field(
        gt=0,
        le=50,
        description="Average bedrooms per household.",
    )

    Population: float = Field(
        gt=0,
        le=100000,
        description="Census block-group population.",
    )

    AveOccup: float = Field(
        gt=0,
        le=1000,
        description="Average household occupancy.",
    )

    Latitude: float = Field(
        ge=32,
        le=42,
        description="California block-group latitude.",
    )

    Longitude: float = Field(
        ge=-125,
        le=-113,
        description="California block-group longitude.",
    )

    @model_validator(mode="after")
    def validate_feature_relationships(self) -> Self:
        if self.AveBedrms > self.AveRooms:
            raise ValueError(
                "AveBedrms cannot be greater than AveRooms."
            )

        return self


class PredictionResponse(BaseModel):

    predicted_value: float
    predicted_value_usd: float
    warning: str


@app.get(
        "/health",
        status_code=200,
)
def health(response: Response):
    model_loaded = predictor is not None

    if not model_loaded:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": (
            "healthy"
            if model_loaded
            else "unhealthy"
        ),
        "model_loaded": model_loaded,
        "model_version": (
            predictor.model_version
            if model_loaded
            else None
        ),
        "data_version": (
            predictor.data_version
            if model_loaded
            else None
        ),
    }


@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(features: HousingFeatures,) -> PredictionResponse:
    logger.info("Prediction request received")

    if predictor is None:
        logger.error(
            "Prediction requested while model is not loaded"
        )

        raise HTTPException(
            status_code=503,
            detail="The prediction model is currently unavailable.",
        )
    
    try:
        prediction = predictor.predict(
            features.model_dump()
        )

        logger.info(
            "Prediction completed successfully"
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

    except ValueError as exception:
        logger.warning(
            "Prediction input failed inference validation: %s",
            exception,
        )

        raise HTTPException(
            status_code=400,
            detail=str(exception),
        ) from exception    

    except Exception:
        logger.exception(
            "Prediction failed"
        )
        raise HTTPException(
            status_code=500,
            detail="Unable to generate predictions"
        )