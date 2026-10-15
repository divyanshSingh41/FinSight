from langchain_core.tools import tool

from backend.app.tools.market_data import get_stock_data, supported_tickers 
from backend.app.quant.metrics import (
    calculate_price_cagr,
    calculate_total_returns,
    calculate_volatility,
    calculate_maximum_drawdown,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_calmar_ratio,
)

@tool
def fetch_data(ticker: str, start_date: str, end_date: str) -> dict:
    """
    Fetch historical stock data for a given ticker symbol between specified dates.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple).
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
        dict: A dictionary containing the historical stock data and metadata.
    """
    return get_stock_data(ticker, start_date, end_date)

@tool
def compute_cagr(prices: list[float]) -> float:
    """
    Calculate the Compound Annual Growth Rate (CAGR) of a stock based on its price series.

    Args:
        prices (list[float]): A list of stock prices.

    Returns:
        float: The CAGR as a decimal (e.g., 0.10 for 10%).
    """
    import pandas as pd
    price_series = pd.Series(prices)
    return calculate_price_cagr(price_series)

@tool
def compute_total_returns(prices: list[float], dividends: list[float] = None) -> float:
    """
    Calculate the total returns of a stock based on its price series and optional dividend series.

    Args:
        prices (list[float]): A list of stock prices.
        dividends (list[float], optional): A list of dividends corresponding to the price series. Defaults to None.

    Returns:
        float: The total returns as a decimal (e.g., 0.10 for 10%).
    """
    import pandas as pd
    price_series = pd.Series(prices)
    dividend_series = pd.Series(dividends) if dividends is not None else None
    return calculate_total_returns(price_series, dividend_series)

@tool
def compute_volatility(prices: list[float]) -> float:
    """
    Calculate the volatility of a stock based on its price series.

    Args:
        prices (list[float]): A list of stock prices.

    Returns:
        float: The volatility as a decimal (e.g., 0.10 for 10%).
    """
    import pandas as pd
    price_series = pd.Series(prices)
    return calculate_volatility(price_series)


@tool
def analyze_stock_performance(
    ticker: str,
    start_date: str,
    end_date: str,
) -> dict:
    """Analyze a supported Indian stock over a date range.
    Fetches historical prices and calculates total price return,
    CAGR, annualized volatility, and maximum drawdown in Python.
    Returns compact metrics rather than the full price history.
    Dividends are excluded from the return calculations.
    """
    import math
    import pandas as pd
    from datetime import datetime
    from backend.app.quant.metrics import (
        calculate_price_cagr,
        calculate_total_returns,
        calculate_volatility,
    )

    result = get_stock_data(ticker, start_date, end_date)
    data = result["data"]

    if isinstance(data, pd.DataFrame):
        prices = data["close"].astype(float).tolist()
        dates = pd.to_datetime(data["date"])
    else:
        prices = [float(row["close"]) for row in data]
        dates = pd.to_datetime([row["date"] for row in data])

    price_series = pd.Series(prices, index=pd.DatetimeIndex(dates),dtype=float)

    maximum_drawdown = calculate_maximum_drawdown(price_series)
    sharpe_ratio = calculate_sharpe_ratio(
        price_series,
        annual_risk_free_rate=0.0,
    )
    sortino_ratio = calculate_sortino_ratio(
        price_series,
        annual_target_return=0.0,
    )
    calmar_ratio = calculate_calmar_ratio(price_series)

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    years = (end - start).days / 365.25

    if years <= 0:
        raise ValueError("end_date must be after start_date.")

    cagr = calculate_price_cagr(price_series)
    total_return = calculate_total_returns(price_series)
    volatility = calculate_volatility(price_series)

    return {
        "ticker": result["symbol"],
        "period": f"{start_date} to {end_date}",
        "observations": len(prices),
        "first_price": round(prices[0], 2),
        "last_price": round(prices[-1], 2),
        "total_price_return": total_return,
        "cagr": cagr,
        "volatility": volatility,
        "maximum_drawdown": maximum_drawdown,
        "sharpe_ratio": sharpe_ratio,
        "sortino_ratio": sortino_ratio,
        "calmar_ratio": calmar_ratio,
        "classification": "CALCULATED",
        "note": "Price-based metrics; dividends are excluded.",
    }


FINANCIAL_TOOLS = [analyze_stock_performance]
