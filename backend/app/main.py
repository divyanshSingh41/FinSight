import logging
from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, model_validator

from backend.app.agents.research_graph import run_research
from backend.app.tools.market_data import supported_tickers

logger = logging.getLogger(__name__)

app = FastAPI(
    title="FinSight API",
    description="API for FinSight financial research",
    version="1.0.0",
)

# Allow the local Vite frontend to call FastAPI directly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class AnalysisRequest(BaseModel):
    question: str = Field(min_length=5, max_length=4000)
    ticker: str | None = None
    fiscal_year: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, value: str | None) -> str | None:
        if value is None:
            return None

        ticker = value.strip().upper()
        if ticker not in supported_tickers:
            supported = ", ".join(sorted(supported_tickers))
            raise ValueError(f"Unsupported ticker. Supported tickers: {supported}")

        return ticker

    @model_validator(mode="after")
    def validate_date_range(self):
        if (self.start_date is None) != (self.end_date is None):
            raise ValueError("Provide both start_date and end_date, or neither.")

        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date <= self.start_date
        ):
            raise ValueError("end_date must be after start_date.")

        return self


class AnalysisResponse(BaseModel):
    ticker: str | None
    fiscal_year: str | None
    report: str


@app.get("/")
def home():
    return {"message": "FinSight API is running"}


@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/v1/analysis", response_model=AnalysisResponse)
def analyze_company(request: AnalysisRequest):
    try:
        report = run_research(
            question=request.question,
            ticker=request.ticker,
            fiscal_year=request.fiscal_year,
            start_date=(
                request.start_date.isoformat()
                if request.start_date
                else None
            ),
            end_date=(
                request.end_date.isoformat()
                if request.end_date
                else None
            ),
        )

        return AnalysisResponse(
            ticker=request.ticker,
            fiscal_year=request.fiscal_year,
            report=report,
        )

    except Exception as exc:
        logger.exception("Research workflow failed")
        raise HTTPException(
            status_code=500,
            detail="Analysis failed. Check the backend logs.",
        ) from exc