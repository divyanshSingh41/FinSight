import yfinance as yf
import pandas as pd

supported_tickers = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
}

def get_stock_data(ticker : str, start_date : str, end_date : str) -> dict:
    """
    Fetch historical stock data for a given ticker symbol between specified dates.

    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple).
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
        pandas.DataFrame: A DataFrame containing the historical stock data.
    """
    ticker = ticker.strip().upper()  # Ensure ticker is in uppercase
    symbol = next(
        (
            yahoo_ticker
            for company, yahoo_ticker in supported_tickers.items()
            if ticker == company or ticker == yahoo_ticker
        ),
        None,
    )
    if symbol is None:
        raise ValueError(
            f"Unsupported ticker: {ticker}. "
            f"Supported companies: {', '.join(supported_tickers)}"
        )

    
    stock = yf.Ticker(symbol)
    data = stock.history(start=start_date, end=end_date)
    if data.empty:
        raise ValueError(f"No data found for ticker '{ticker}' between {start_date} and {end_date}.")
    data = data.reset_index()  # Reset index to have 'Date' as a column
    return {
        "symbol": ticker,
        "start_date": start_date,
        "end_date": end_date,
        "period": f"{start_date} to {end_date}",    
        "currency": stock.info.get("currency", "N/A"),  
        "data": [
        {
            "date": row["Date"].strftime("%Y-%m-%d"),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"])
        }
        for _, row in data.iterrows()
        ]
        }

def compare_stock_history(companies: list[str], period: str = "5y") -> dict:
    """Fetch historical prices for multiple supported companies."""

    results = {}
    errors = {}

    for company in companies:
        company = company.upper()

        if company not in supported_tickers:
            errors[company] = "Unsupported company"
            continue

        try:
            results[company] = get_stock_data(company, period)
        except Exception as exc:
            errors[company] = str(exc)

    return {
        "period": period,
        "results": results,
        "errors": errors,
    }


if __name__ == "__main__":
    result = get_stock_data("RELIANCE.NS", "2023-01-01", "2023-12-31")
    print("Company:", result["symbol"])
    print("Data Type:", type(result["data"]))
    print("Records:", len(result["data"]))
    print("Latest:", result["data"][-1])



