import streamlit as st
from solar_calculator import calculate_solar_requirements
from excel_writer import generate_excel_report

DEMO_EXTRACTED = {
    "consumer_name":       "Rajesh Kumar Sharma",
    "consumer_number":     "220011234567",
    "meter_number":        "MH123456789",
    "billing_address":     "Plot No. 45, Sector 7, Pimpri-Chinchwad, Pune - 411018",
    "billing_month":       "March 2024",
    "billing_period_from": "01/03/2024",
    "billing_period_to":   "31/03/2024",
    "tariff_category":     "LT-1 Residential",
    "sanctioned_load_kw":  5.0,
    "contract_demand_kva": None,
    "units_consumed_kwh":  320,
    "previous_reading":    12450,
    "current_reading":     12770,
    "number_of_days":      30,
    "total_bill_amount":   3200,
    "energy_charges":      2560,
    "fixed_charges":       400,
    "tax_amount":          240,
    "power_factor":        None,
    "distribution_company": "MSEDCL",
    "phase_type":          "Single Phase",
    "monthly_avg_units":   310,
}

st.set_page_config(
    page_title="Energybae Demo",
    page_icon="☀️",
    layout="wide"
)

st.markdown("## ☀️ Energybae Solar Calculator — DEMO MODE")
st.info("🔵 This demo uses sample MSEDCL bill data — no API key needed")

if st.button("▶️ Run Demo Calculation", type="primary"):
    calcs       = calculate_solar_requirements(DEMO_EXTRACTED)
    excel_bytes = generate_excel_report(DEMO_EXTRACTED, calcs)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Solar Size",    f"{calcs['solar_kwp_recommended']} kWp")
    c2.metric("Panels",        f"{calcs['num_panels_400wp']} nos")
    c3.metric("Annual Saving", f"Rs {calcs['annual_savings_inr']:,.0f}")
    c4.metric("Payback",       f"{calcs['payback_period_years']} yrs")

    st.markdown("### Full Calculation Results")
    st.json(calcs)

    st.download_button(
        label="⬇️ Download Demo Excel Report",
        data=excel_bytes,
        file_name="Energybae_Solar_Demo_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )