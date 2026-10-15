import pandas as pd

def calculate_total_returns(prices: pd.Series) -> float:
    """
    Calculate the total returns of a stock based on its price series.

    Args:
        prices (pd.Series): A pandas Series containing the stock prices.        dividends (pd.Series | None): A pandas Series containing the dividend payments or None.

    Returns:
        float: The total returns as a decimal (e.g., 0.25 for 25%).
    """
    # 1. Validate prices
    if prices is None or len(prices) < 2:
        raise ValueError("At least two valid prices are required.")

    if prices.isna().any():
        raise ValueError("Prices must not contain missing values.")

    if (prices <= 0).any():
        raise ValueError("All prices must be greater than zero.")

    # Sort indices to ensure start and end positions match chronological timeline
    prices = prices.sort_index()

    initial_price = prices.iloc[0]
    final_price = prices.iloc[-1]

    start_date = prices.index[0]
    end_date = prices.index[-1]
    
    # 4. Final Calculation
    total_returns = ((final_price - initial_price)) / initial_price
    return float(total_returns)


def calculate_price_cagr(prices: pd.Series) -> float:
    """
    Calculate the Compound Annual Growth Rate (CAGR) of a stock based on its price series.

    Args:
        prices (pd.Series): A pandas Series containing the stock prices.

    Returns:
        float: The CAGR as a decimal (e.g., 0.10 for 10%).
    """
    # 1. Validate prices
    if prices is None or len(prices) < 2:
        raise ValueError("At least two valid prices are required.")

    if prices.isna().any():
        raise ValueError("Prices must not contain missing values.")

    if (prices <= 0).any():
        raise ValueError("All prices must be greater than zero.")

    # Sort indices to ensure start and end positions match chronological timeline
    prices = prices.sort_index()

    initial_price = prices.iloc[0]
    final_price = prices.iloc[-1]

    # 2. Calculate the number of years between the first and last price
    start_date = prices.index[0]
    end_date = prices.index[-1]
    
    # Ensure that the index is a datetime type for accurate year calculation
    if not pd.api.types.is_datetime64_any_dtype(prices.index):
        raise TypeError("Price index must be of datetime type.")

    years = (end_date - start_date).days / 365.25  # Using average year length to account for leap years

    if years <= 0:
        raise ValueError("The time span between the first and last price must be greater than zero.")

    # 3. Final Calculation
    cagr = (final_price / initial_price) ** (1 / years) - 1
    return float(cagr)


def calculate_volatility(prices: pd.Series) -> float:
    """
    Calculate the annualized volatility of a stock based on its price series.

    Args:
        prices (pd.Series): A pandas Series containing the stock prices.

    Returns:
        float: The annualized volatility as a decimal (e.g., 0.20 for 20%).
    """
    # 1. Validate prices
    if prices is None or len(prices) < 2:
        raise ValueError("At least two valid prices are required.")

    if prices.isna().any():
        raise ValueError("Prices must not contain missing values.")

    if (prices <= 0).any():
        raise ValueError("All prices must be greater than zero.")
    # Sort indices to ensure start and end positions match chronological timeline
    prices = prices.sort_index()
    # 2. Calculate daily returns
    daily_returns = prices.pct_change().dropna()
    # 3. Calculate annualized volatility
    annualized_volatility = daily_returns.std() * (252 ** 0.5)  # Assuming 252 trading days in a year
    return float(annualized_volatility)

def calculate_maximum_drawdown(prices: pd.Series) -> float:
    """Return the largest peak-to-trough price decline as a negative decimal."""
    if prices is None or len(prices) < 2:
        raise ValueError("At least two valid prices are required.")
    if prices.isna().any():
        raise ValueError("Prices must not contain missing values.")
    if (prices <= 0).any():
        raise ValueError("All prices must be greater than zero.")

    prices = prices.sort_index()
    drawdowns = prices / prices.cummax() - 1
    return float(drawdowns.min())


def _validated_daily_returns(prices: pd.Series) -> pd.Series:
    if prices is None or len(prices) < 3:
        raise ValueError("At least three valid prices are required.")
    if prices.isna().any():
        raise ValueError("Prices must not contain missing values.")
    if (prices <= 0).any():
        raise ValueError("All prices must be greater than zero.")

    return prices.sort_index().pct_change().dropna()


def calculate_sharpe_ratio(
    prices: pd.Series,
    annual_risk_free_rate: float = 0.0,
) -> float | None:
    """
    Calculate annualized Sharpe ratio.
    Rates are decimals: 0.05 means 5%. Defaults to a 0% risk-free rate.
    Returns None when daily returns have zero volatility.
    """
    if annual_risk_free_rate <= -1:
        raise ValueError("Annual risk-free rate must be greater than -1.")

    daily_returns = _validated_daily_returns(prices)
    daily_risk_free_rate = (1 + annual_risk_free_rate) ** (1 / 252) - 1
    excess_returns = daily_returns - daily_risk_free_rate
    daily_volatility = float(excess_returns.std(ddof=1))

    if daily_volatility == 0:
        return None

    return float(
        excess_returns.mean() / daily_volatility * (252 ** 0.5)
    )


def calculate_sortino_ratio(
    prices: pd.Series,
    annual_target_return: float = 0.0,
) -> float | None:
    """
    Calculate annualized Sortino ratio.
    Rates are decimals: 0.05 means 5%. Defaults to a 0% target return.
    Returns None when there are no returns below the target.
    """
    if annual_target_return <= -1:
        raise ValueError("Annual target return must be greater than -1.")

    daily_returns = _validated_daily_returns(prices)
    daily_target = (1 + annual_target_return) ** (1 / 252) - 1
    excess_returns = daily_returns - daily_target
    downside_returns = excess_returns.clip(upper=0)
    downside_deviation = float((downside_returns ** 2).mean() ** 0.5)

    if downside_deviation == 0:
        return None

    return float(
        excess_returns.mean() / downside_deviation * (252 ** 0.5)
    )


def calculate_calmar_ratio(prices: pd.Series) -> float | None:
    """
    Calculate CAGR divided by the absolute maximum drawdown.
    Returns None when the price series has no drawdown.
    """
    maximum_drawdown = calculate_maximum_drawdown(prices)

    if maximum_drawdown == 0:
        return None

    return float(
        calculate_price_cagr(prices) / abs(maximum_drawdown)
    )