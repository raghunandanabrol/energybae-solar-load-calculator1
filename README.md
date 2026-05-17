# energybae-solar-load-calculator1
AI-powered automation system using Python, Streamlit, and Groq Vision AI that converts a customer's electricity bill into a complete solar load calculation Excel report in under 60 seconds and it provides the excel report with solar sizing, savings, ROI, and 25-year projection charts.
# ☀️ Energybae Solar Load Calculator

AI-powered automation system that converts electricity bills 
into solar load calculation Excel reports.

## 🚀 What It Does

- Upload electricity bill (PDF or image)
- AI reads and extracts bill data automatically
- Calculates solar system size, savings, ROI
- Generates professional Excel report

## 🛠️ Tech Stack

- Python
- Streamlit
- Groq Vision AI
- pdfplumber
- Pillow
- openpyxl

## ⚡ How To Run

### 1. Clone the repository
git clone https://github.com/yourusername/energybae-solar-calculator1.git
cd energybae-solar-calculator

### 2. Install libraries
pip install -r requirements.txt

### 3. Add API key
Create .env file and add:
GROQ_API_KEY=your_groq_api_key_here

### 4. Run the app
streamlit run app.py

## 📊 Excel Report Includes

- Customer bill details
- Solar system size (kWp)
- Number of panels
- Annual savings
- Government subsidy
- 25-year ROI projection
- Savings chart
