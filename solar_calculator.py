import math


def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return default


def calculate_solar_requirements(extracted_data: dict) -> dict:

    # ── Input Values ──────────────────────────────────────────
    units_kwh       = safe_float(extracted_data.get("units_consumed_kwh"))
    days            = safe_float(extracted_data.get("number_of_days"), 30)
    sanctioned_load = safe_float(extracted_data.get("sanctioned_load_kw"))
    total_bill      = safe_float(extracted_data.get("total_bill_amount"))
    tariff_category = extracted_data.get("tariff_category", "Residential")
    monthly_avg     = safe_float(extracted_data.get("monthly_avg_units"))

    # ── Daily & Monthly Consumption ───────────────────────────
    daily_consumption_kwh = units_kwh / days if days > 0 else units_kwh / 30
    monthly_consumption_kwh = monthly_avg if monthly_avg > 0 else daily_consumption_kwh * 30

    # ── Solar Sizing ──────────────────────────────────────────
    peak_sun_hours = 4.5
    system_eff     = 0.80

    solar_kwp_required    = daily_consumption_kwh / (peak_sun_hours * system_eff)
    solar_kwp_recommended = math.ceil(solar_kwp_required * 2) / 2

    # ── Panels & Inverter ─────────────────────────────────────
    panel_watt  = 400
    num_panels  = math.ceil((solar_kwp_recommended * 1000) / panel_watt)
    inverter_kva = math.ceil(solar_kwp_recommended / 0.8 * 2) / 2

    # ── Generation ────────────────────────────────────────────
    annual_generation_kwh = solar_kwp_recommended * peak_sun_hours * 365 * system_eff

    # ── Per Unit Rate ─────────────────────────────────────────
    if units_kwh > 0 and total_bill > 0:
        per_unit_rate = total_bill / units_kwh
    else:
        per_unit_rate = 8.5
    per_unit_rate = max(4.0, min(per_unit_rate, 15.0))

    # ── Savings ───────────────────────────────────────────────
    annual_savings_inr = annual_generation_kwh * per_unit_rate

    # ── System Cost ───────────────────────────────────────────
    cost_per_kwp      = 45000
    total_system_cost = solar_kwp_recommended * cost_per_kwp

    # ── Payback & ROI ─────────────────────────────────────────
    payback_years  = total_system_cost / annual_savings_inr if annual_savings_inr > 0 else 0
    roi_percent_25yr = (
        (annual_savings_inr * 25 - total_system_cost) / total_system_cost * 100
        if total_system_cost > 0 else 0
    )

    # ── Environment ───────────────────────────────────────────
    co2_saved_kg_annual = annual_generation_kwh * 0.716
    trees_equivalent    = co2_saved_kg_annual / 21.77

    # ── Subsidy ───────────────────────────────────────────────
    if "residential" in str(tariff_category).lower() or "lt-1" in str(tariff_category).lower():
        if solar_kwp_recommended <= 2:
            subsidy = solar_kwp_recommended * 30000
        elif solar_kwp_recommended <= 3:
            subsidy = 2 * 30000 + (solar_kwp_recommended - 2) * 18000
        else:
            subsidy = 78000
    else:
        subsidy = 0

    net_cost_after_subsidy = total_system_cost - subsidy

    # ── Coverage ──────────────────────────────────────────────
    solar_coverage_pct = min(
        (annual_generation_kwh / (monthly_consumption_kwh * 12)) * 100, 100
    ) if monthly_consumption_kwh > 0 else 0

    return {
        "monthly_consumption_kwh":  round(monthly_consumption_kwh, 2),
        "daily_consumption_kwh":    round(daily_consumption_kwh, 2),
        "per_unit_rate_inr":        round(per_unit_rate, 2),
        "monthly_bill_inr":         round(total_bill, 2),
        "solar_kwp_required":       round(solar_kwp_required, 2),
        "solar_kwp_recommended":    round(solar_kwp_recommended, 1),
        "num_panels_400wp":         num_panels,
        "inverter_size_kva":        inverter_kva,
        "annual_generation_kwh":    round(annual_generation_kwh, 0),
        "solar_coverage_pct":       round(solar_coverage_pct, 1),
        "total_system_cost_inr":    round(total_system_cost, 0),
        "govt_subsidy_inr":         round(subsidy, 0),
        "net_cost_after_subsidy":   round(net_cost_after_subsidy, 0),
        "annual_savings_inr":       round(annual_savings_inr, 0),
        "payback_period_years":     round(payback_years, 1),
        "roi_25_years_pct":         round(roi_percent_25yr, 1),
        "co2_saved_kg_annual":      round(co2_saved_kg_annual, 0),
        "trees_equivalent":         round(trees_equivalent, 0),
        "peak_sun_hours":           peak_sun_hours,
        "system_efficiency_pct":    system_eff * 100,
    }