import math

import pandas as pd

from backend.app.quant.metrics import (
    calculate_price_cagr,
    calculate_total_returns,
    calculate_volatility,
)


def _valid_unique_facts(facts: list[dict]) -> tuple[dict, set[str]]:
    values = {}
    conflicts = set()

    for fact in facts:
        metric = fact["metric"]
        value = float(fact["value"])

        if metric in values and not math.isclose(
            values[metric]["value"], value, rel_tol=1e-9, abs_tol=1e-9
        ):
            conflicts.add(metric)
        else:
            values[metric] = fact

    for metric in conflicts:
        values.pop(metric, None)

    return values, conflicts


def _calculate_statement_ratios(facts: list[dict]) -> list[dict]:
    # Ratios are grouped by period, accounting basis, and unit.
    groups = {}
    for fact in facts:
        key = (fact["fiscal_year"], fact["basis"], fact["unit"])
        groups.setdefault(key, []).append(fact)

    results = []

    for (fiscal_year, basis, unit), group_facts in groups.items():
        values, conflicts = _valid_unique_facts(group_facts)

        def add_ratio(name, numerator, denominator, formula):
            if numerator not in values or denominator not in values:
                return

            denominator_value = values[denominator]["value"]
            if denominator_value == 0:
                return

            value = values[numerator]["value"] / denominator_value
            if name.endswith("_margin"):
                value *= 100

            results.append({
                "metric": name,
                "value": round(value, 6),
                "fiscal_year": fiscal_year,
                "basis": basis,
                "formula": formula,
                "inputs": {
                    numerator: values[numerator]["value"],
                    denominator: values[denominator]["value"],
                },
                "unit": "%" if name.endswith("_margin") else "ratio",
                "sources": [
                    {
                        "page_number": values[numerator].get("page_number"),
                        "source_url": values[numerator].get("source_url"),
                        "quote": values[numerator].get("evidence_quote"),
                    },
                    {
                        "page_number": values[denominator].get("page_number"),
                        "source_url": values[denominator].get("source_url"),
                        "quote": values[denominator].get("evidence_quote"),
                    },
                ],
                "classification": "CALCULATED",
            })

        add_ratio(
            "operating_margin",
            "operating_profit",
            "revenue",
            "operating_profit / revenue * 100",
        )
        add_ratio(
            "net_profit_margin",
            "net_income",
            "revenue",
            "net_income / revenue * 100",
        )
        add_ratio(
            "debt_to_equity",
            "total_borrowings",
            "total_equity",
            "total_borrowings / total_equity",
        )
        add_ratio(
            "current_ratio",
            "current_assets",
            "current_liabilities",
            "current_assets / current_liabilities",
        )
        add_ratio(
            "cash_flow_to_net_income",
            "cash_from_operations",
            "net_income",
            "cash_from_operations / net_income",
        )

        if (
            "cash_from_operations" in values
            and "capital_expenditure" in values
        ):
            cfo = values["cash_from_operations"]
            capex = values["capital_expenditure"]

            results.append({
                "metric": "free_cash_flow",
                "value": round(cfo["value"] - capex["value"], 6),
                "fiscal_year": fiscal_year,
                "basis": basis,
                "formula": "cash_from_operations - capital_expenditure",
                "inputs": {
                    "cash_from_operations": cfo["value"],
                    "capital_expenditure": capex["value"],
                },
                "unit": unit,
                "sources": [
                    {
                        "page_number": cfo.get("page_number"),
                        "source_url": cfo.get("source_url"),
                        "quote": cfo.get("evidence_quote"),
                    },
                    {
                        "page_number": capex.get("page_number"),
                        "source_url": capex.get("source_url"),
                        "quote": capex.get("evidence_quote"),
                    },
                ],
                "classification": "CALCULATED",
            })

        if conflicts:
            results.append({
                "metric": "validation_warning",
                "message": (
                    "Conflicting extracted values were omitted for: "
                    + ", ".join(sorted(conflicts))
                ),
                "fiscal_year": fiscal_year,
                "basis": basis,
            })

    return results


def run_quant_agent(state: dict) -> dict:
    """Calculate stock metrics and financial ratios from validated inputs."""
    market_results = {}

    market_data = state.get("market_data")
    if market_data and market_data.get("data"):
        rows = market_data["data"]
        prices = pd.Series(
            [float(row["close"]) for row in rows],
            index=pd.to_datetime([row["date"] for row in rows]),
            dtype=float,
        ).sort_index()

        market_results = {
            "ticker": market_data["symbol"],
            "period": market_data["period"],
            "currency": market_data.get("currency"),
            "total_price_return": calculate_total_returns(prices),
            "cagr": calculate_price_cagr(prices),
            "annualized_volatility": calculate_volatility(prices),
            "maximum_drawdown": float((prices / prices.cummax() - 1).min()),
            "classification": "CALCULATED",
            "note": "Price-based returns; dividends are excluded.",
        }

    statement_ratios = _calculate_statement_ratios(
        state.get("financial_facts", [])
    )

    return {
        "quant_results": {
            "market_metrics": market_results,
            "financial_metrics": statement_ratios,
        }
    }