

import streamlit as st
import os
from dotenv import load_dotenv
from extractor import extract_bill_data
from solar_calculator import calculate_solar_requirements
from excel_writer import generate_excel_report
from datetime import datetime

# Load .env file
load_dotenv()

# ── Page setup ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Energybae Solar Calculator",
    page_icon="☀️",
    layout="wide"
)

# ── Page styling ──────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #F1F8E9; }
    .title-box {
        background: linear-gradient(135deg, #1B5E20, #388E3C);
        color: white; padding: 25px 30px;
        border-radius: 12px; text-align: center; margin-bottom: 20px;
    }
    .title-box h1 { color: white; font-size: 2.2rem; margin: 0; }
    .title-box p  { color: #C8E6C9; font-size: 1rem; margin: 5px 0 0; }
    div[data-testid="metric-container"] {
        background: white; border: 1px solid #C8E6C9;
        border-radius: 8px; padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────
st.markdown("""
<div class="title-box">
    <h1>☀️ ENERGYBAE — Solar Load Calculator</h1>
    <p>Upload your electricity bill and get instant solar sizing + Excel report</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    # Groq API Key input
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        value=os.getenv("GROQ_API_KEY", ""),
        help="Get FREE key from console.groq.com"
    )

    # Show key status
    if api_key:
        st.success("✅ API Key loaded")
    else:
        st.warning("⚠️ Enter Groq API Key")

    st.markdown("---")
    st.markdown("### 📖 How It Works")
    st.markdown("""
    1. Upload your electricity bill
    2. Groq AI reads key data
    3. Solar size is calculated
    4. Excel report is generated
    5. Download your report
    """)

    st.markdown("---")
    st.markdown("### 🆓 Powered By")
    st.markdown("Groq AI — FREE & Fast")
    st.markdown("No charges at all!")
    st.markdown("14,400 requests/day free!")

    st.markdown("---")
    st.markdown("energybae.co@gmail.com")
    st.markdown("+91 9112233120")
    st.markdown("www.energybae.in")

# ── Upload & Process ──────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📤 Step 1: Upload Electricity Bill")
    uploaded_file = st.file_uploader(
        "Upload PDF or Image",
        type=["pdf", "png", "jpg", "jpeg", "webp"],
        help="Upload MSEDCL or any Indian electricity bill"
    )

    if uploaded_file:
        st.success(
            f"✅ File uploaded: {uploaded_file.name} "
            f"({uploaded_file.size // 1024} KB)"
        )
        if uploaded_file.type.startswith("image"):
            st.image(
                uploaded_file,
                caption="Bill Preview",
                use_column_width=True
            )
        else:
            st.info("📄 PDF uploaded — will be processed by Groq AI")

with col2:
    st.markdown("### ⚙️ Step 2: Process & Calculate")

    if uploaded_file and api_key:
        if st.button(
            "🚀 Extract & Calculate Solar",
            use_container_width=True,
            type="primary"
        ):

            # Set Groq API key in environment
            os.environ["GROQ_API_KEY"] = api_key

            # Step A — Extract data from bill
            with st.spinner("🤖 Groq AI is reading your bill..."):
                try:
                    file_bytes = uploaded_file.read()
                    file_type  = (
                        "pdf"
                        if uploaded_file.type == "application/pdf"
                        else "image"
                    )

                    # Call extractor
                    extracted = extract_bill_data(
                        file_bytes,
                        file_type
                    )
                    st.session_state["extracted"] = extracted
                    st.success("✅ Data extracted successfully!")

                except Exception as e:
                    st.error(f"❌ Extraction failed: {str(e)}")
                    st.stop()

            # Step B — Calculate solar requirements
            with st.spinner("☀️ Calculating solar requirements..."):
                try:
                    calcs = calculate_solar_requirements(
                        st.session_state["extracted"]
                    )
                    st.session_state["calcs"] = calcs
                    st.success("✅ Solar calculation complete!")

                except Exception as e:
                    st.error(f"❌ Calculation failed: {str(e)}")
                    st.stop()

            # Step C — Generate Excel report
            with st.spinner("📊 Generating Excel report..."):
                try:
                    excel_bytes = generate_excel_report(
                        st.session_state["extracted"],
                        st.session_state["calcs"]
                    )
                    st.session_state["excel_bytes"] = excel_bytes
                    st.success("✅ Excel report ready!")

                except Exception as e:
                    st.error(f"❌ Excel generation failed: {str(e)}")

    elif not api_key:
        st.warning(
            "⚠️ Please enter your Groq API Key in the sidebar.\n\n"
            "Get FREE key from: console.groq.com"
        )

    elif not uploaded_file:
        st.info("👈 Please upload an electricity bill first.")

# ── Results ───────────────────────────────────────────────────────────
if ("extracted" in st.session_state and
        "calcs" in st.session_state):

    extracted = st.session_state["extracted"]
    calcs     = st.session_state["calcs"]

    st.markdown("---")
    st.markdown("## 📊 Results")

    # 5 Key metric boxes
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("☀️ Solar System Size",
              f"{calcs['solar_kwp_recommended']} kWp")
    m2.metric("🔲 No. of Panels",
              f"{calcs['num_panels_400wp']} panels")
    m3.metric("💰 Annual Savings",
              f"Rs {calcs['annual_savings_inr']:,.0f}")
    m4.metric("📅 Payback Period",
              f"{calcs['payback_period_years']} years")
    m5.metric("🌱 CO2 Saved/Year",
              f"{calcs['co2_saved_kg_annual']:,.0f} kg")

    # Detailed tabs
    tab1, tab2, tab3 = st.tabs([
        "📋 Bill Data Extracted",
        "☀️ Solar Sizing",
        "💰 Financial Analysis"
    ])

    # TAB 1 — Bill Data
    with tab1:
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**👤 Customer Details**")
            for k, v in [
                ("Consumer Name",   extracted.get("consumer_name")),
                ("Consumer No.",    extracted.get("consumer_number")),
                ("Meter No.",       extracted.get("meter_number")),
                ("Address",         extracted.get("billing_address")),
                ("DISCOM",          extracted.get("distribution_company")),
                ("Phase",           extracted.get("phase_type")),
                ("Tariff Category", extracted.get("tariff_category")),
            ]:
                st.markdown(f"**{k}:** {v or 'N/A'}")

        with col_b:
            st.markdown("**📄 Bill Details**")
            for k, v in [
                ("Billing Month",
                 extracted.get("billing_month")),
                ("Days",
                 extracted.get("number_of_days")),
                ("Units Consumed",
                 f"{extracted.get('units_consumed_kwh')} kWh"),
                ("Sanctioned Load",
                 f"{extracted.get('sanctioned_load_kw')} kW"),
                ("Energy Charges",
                 f"Rs {extracted.get('energy_charges')}"),
                ("Total Bill Amount",
                 f"Rs {extracted.get('total_bill_amount')}"),
            ]:
                st.markdown(f"**{k}:** {v or 'N/A'}")

    # TAB 2 — Solar Sizing
    with tab2:
        col_c, col_d = st.columns(2)

        with col_c:
            st.markdown("**📊 Your Consumption**")
            st.info(
                f"Monthly: {calcs['monthly_consumption_kwh']} kWh"
            )
            st.info(
                f"Daily: {calcs['daily_consumption_kwh']} kWh/day"
            )
            st.info(
                f"Rate: Rs {calcs['per_unit_rate_inr']}/kWh"
            )

        with col_d:
            st.markdown("**⚡ Recommended System**")
            st.success(
                f"Size: {calcs['solar_kwp_recommended']} kWp"
            )
            st.success(
                f"Panels: {calcs['num_panels_400wp']} x 400Wp"
            )
            st.success(
                f"Inverter: {calcs['inverter_size_kva']} kVA"
            )
            st.success(
                f"Generates: {calcs['annual_generation_kwh']:,.0f} kWh/yr"
            )
            st.success(
                f"Coverage: {calcs['solar_coverage_pct']}%"
            )

    # TAB 3 — Financials
    with tab3:
        col_e, col_f = st.columns(2)

        with col_e:
            st.markdown("**💸 Investment**")
            st.metric("System Cost",
                      f"Rs {calcs['total_system_cost_inr']:,.0f}")
            st.metric("Govt. Subsidy",
                      f"Rs {calcs['govt_subsidy_inr']:,.0f}")
            st.metric("Net Investment",
                      f"Rs {calcs['net_cost_after_subsidy']:,.0f}")

        with col_f:
            st.markdown("**📈 Returns**")
            st.metric("Annual Savings",
                      f"Rs {calcs['annual_savings_inr']:,.0f}")
            st.metric("Payback Period",
                      f"{calcs['payback_period_years']} years")
            st.metric("25-Year ROI",
                      f"{calcs['roi_25_years_pct']}%")
            st.metric(
                "25 Year Total Saving",
                f"Rs {round(calcs['annual_savings_inr'] * 25, 0):,.0f}"
            )

    # ── Download ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📥 Step 3: Download Your Report")

    if "excel_bytes" in st.session_state:
        consumer = extracted.get("consumer_name", "Customer")
        month    = extracted.get(
            "billing_month",
            datetime.now().strftime("%B_%Y")
        )
        filename = (
            f"Energybae_Solar_{consumer}_{month}.xlsx"
            .replace(" ", "_")
        )

        st.download_button(
            label="⬇️ Download Excel Solar Report",
            data=st.session_state["excel_bytes"],
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
        st.success(
            "✅ Your personalized solar report is ready! "
            "Download and share with your customer."
        )

