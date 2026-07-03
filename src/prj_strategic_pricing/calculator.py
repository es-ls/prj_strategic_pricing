from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any


@dataclass(frozen=True)
class PricingResult:
    labor_cost: float
    non_labor_cost: float
    risk_buffer: float
    minimum_margin: float
    price_cost: float
    price_ceiling: float
    price_market: float
    price_anchor: float
    proposed_price: float
    walkaway_price: float
    required_mm: float
    available_mm: float | None
    mm_is_feasible: bool | None
    recommended_floor_gap: float
    warnings: tuple[str, ...]


def calculate_pricing(workbook_data: dict[str, list[dict[str, Any]]]) -> PricingResult:
    rates = _rates_by_grade(workbook_data.get("rates", []))
    wbs_rows = workbook_data.get("wbs", [])
    non_labor_rows = workbook_data.get("non_labor_costs", [])
    value_rows = workbook_data.get("value_market_anchor", [])
    strategy = _key_value(workbook_data.get("strategy", []))

    required_mm = sum(_number(row.get("mm")) for row in wbs_rows)
    labor_cost = sum(
        _number(row.get("mm")) * rates.get(str(row.get("grade", "")).strip(), 0.0)
        for row in wbs_rows
    )
    non_labor_cost = sum(_number(row.get("amount")) for row in non_labor_rows)

    risk_buffer = _amount_or_rate(
        strategy,
        "risk_buffer",
        "risk_buffer_rate",
        labor_cost + non_labor_cost,
    )
    minimum_margin = _amount_or_rate(
        strategy,
        "minimum_margin",
        "minimum_margin_rate",
        labor_cost + non_labor_cost + risk_buffer,
    )
    price_cost = labor_cost + non_labor_cost + risk_buffer + minimum_margin

    value = _key_value(value_rows)
    ceiling_ratio = _number(value.get("ceiling_ratio"), 0.60)
    market_ratio = _number(value.get("market_ratio"), 0.80)
    anchor_annual = _number(value.get("anchor_annual"), 1_000_000_000)
    project_months = _number(value.get("project_months"), _number(strategy.get("project_months"), 12))

    customer_saving = _number(value.get("customer_saving"))
    price_ceiling = customer_saving * ceiling_ratio

    competitor_prices = [
        _number(v)
        for key, v in value.items()
        if key.startswith("competitor_price") and _number(v) > 0
    ]
    price_market = mean(competitor_prices) * market_ratio if competitor_prices else 0.0
    price_anchor = anchor_annual * (project_months / 12)

    proposed_price = _number(strategy.get("proposed_price"))
    if proposed_price <= 0:
        candidates = [price_market, price_anchor, price_ceiling]
        viable = [price for price in candidates if price >= price_cost]
        proposed_price = min(viable) if viable else max(candidates + [price_cost])

    walkaway_multiplier = _number(strategy.get("walkaway_multiplier"), 1.0)
    walkaway_price = _number(strategy.get("walkaway_price"), price_cost * walkaway_multiplier)

    avg_rate = mean(rates.values()) if rates else 0.0
    labor_budget = proposed_price - non_labor_cost
    available_mm = labor_budget / avg_rate if avg_rate > 0 else None
    mm_is_feasible = required_mm <= available_mm if available_mm is not None else None

    warnings: list[str] = []
    if price_cost > price_ceiling > 0:
        warnings.append("Price Cost exceeds Price Ceiling. Consider scope reduction, phase split, or no-go review.")
    if price_market and price_market < price_cost:
        warnings.append("Price Market is below Price Cost. Margin defense requires differentiation or scope change.")
    if proposed_price < walkaway_price:
        warnings.append("Proposed price is below Walk-away Price.")
    if mm_is_feasible is False:
        warnings.append("Required M/M exceeds available M/M under the proposed price.")
    if any(str(row.get("grade", "")).strip() not in rates for row in wbs_rows):
        warnings.append("Some WBS grades do not have a matching monthly rate.")

    return PricingResult(
        labor_cost=labor_cost,
        non_labor_cost=non_labor_cost,
        risk_buffer=risk_buffer,
        minimum_margin=minimum_margin,
        price_cost=price_cost,
        price_ceiling=price_ceiling,
        price_market=price_market,
        price_anchor=price_anchor,
        proposed_price=proposed_price,
        walkaway_price=walkaway_price,
        required_mm=required_mm,
        available_mm=available_mm,
        mm_is_feasible=mm_is_feasible,
        recommended_floor_gap=proposed_price - price_cost,
        warnings=tuple(warnings),
    )


def _rates_by_grade(rows: list[dict[str, Any]]) -> dict[str, float]:
    return {
        str(row.get("grade", "")).strip(): _number(row.get("monthly_rate"))
        for row in rows
        if str(row.get("grade", "")).strip()
    }


def _key_value(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for row in rows:
        key = str(row.get("key", row.get("metric", ""))).strip()
        if key:
            result[key] = row.get("value")
    return result


def _amount_or_rate(values: dict[str, Any], amount_key: str, rate_key: str, base: float) -> float:
    amount = _number(values.get(amount_key))
    if amount:
        return amount
    return base * _number(values.get(rate_key))


def _number(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    if isinstance(value, str):
        return float(value.replace(",", "").replace("KRW", "").strip())
    return float(value)
