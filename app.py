import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import sqlite3
import io
from reportlab.pdfgen import canvas

from rule_based import rule_based_score
from company_check import check_company_credibility
from job_category_risk import job_category_risk
from safety_tips import get_safety_tips


# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Fake Job Detection System", layout="wide")


# ---------------- DATABASE ----------------
conn = sqlite3.connect("history.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS job_history(
id INTEGER PRIMARY KEY AUTOINCREMENT,
job_text TEXT,
ml_score REAL,
rule_score REAL,
final_score REAL
)
""")
conn.commit()


# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "users" not in st.session_state:
    st.session_state.users = {"admin": "admin123"}


# ---------------- LOGIN / REGISTER ----------------
if not st.session_state.logged_in:

    st.title("Fake Job Detection System")

    menu = st.selectbox("Select Option", ["Login", "Register"])

    if menu == "Login":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid username or password")

    if menu == "Register":

        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")

        if st.button("Register"):

            st.session_state.users[new_user] = new_pass
            st.success("Registration successful. Please login.")

    st.stop()


# ---------------- LOAD ML MODEL ----------------
model = joblib.load("job_fraud_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")


# ---------------- PDF GENERATOR ----------------
def generate_pdf(ml, rule, final, reasons, flags):

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    c.drawString(100, 800, "Fake Job Detection Report")

    c.drawString(100, 760, f"ML Probability: {ml:.2f}%")
    c.drawString(100, 740, f"Rule Score: {rule}")
    c.drawString(100, 720, f"Final Risk Score: {final:.2f}%")

    y = 680
    c.drawString(100, y, "Red Flags:")

    for f in flags:
        y -= 20
        c.drawString(120, y, f)

    y -= 30
    c.drawString(100, y, "Reasons:")

    for r in reasons:
        y -= 20
        c.drawString(120, y, r)

    c.save()
    buffer.seek(0)

    return buffer


# ---------------- SIDEBAR ----------------
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    ["Job Checker", "History", "Analytics", "About"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()


# =====================================================
# JOB CHECKER
# =====================================================
if page == "Job Checker":

    st.title("Fake Job Detection Dashboard")

    job_text = st.text_area("Enter Job Description", height=200)

    if st.button("Analyze Job"):

        if job_text.strip() == "":
            st.warning("Please enter job description")

        else:

            X = vectorizer.transform([job_text])
            ml_probability = model.predict_proba(X)[0][1] * 100

            rule_score, red_flags = rule_based_score(job_text)

            final_score = (ml_probability + rule_score) / 2

            category, category_risk = job_category_risk(job_text)

            credibility, cred_score, reasons = check_company_credibility(job_text)

            # SAVE TO DATABASE
            cursor.execute(
                "INSERT INTO job_history (job_text, ml_score, rule_score, final_score) VALUES (?, ?, ?, ?)",
                (job_text, ml_probability, rule_score, final_score)
            )
            conn.commit()

            # METRICS
            col1, col2, col3 = st.columns(3)

            col1.metric("ML Scam Probability", f"{ml_probability:.2f}%")
            col2.metric("Rule Score", f"{rule_score}")
            col3.metric("Final Risk Score", f"{final_score:.2f}%")

            st.progress(int(final_score))

            # RESULT
            st.subheader("Results")

            st.write("Job Category:", category)
            st.write("Category Risk:", category_risk)
            st.write("Company Credibility:", credibility)

            # REASONS
            st.subheader("Reasons")

            if reasons:
                for r in reasons:
                    st.write("-", r)
            else:
                st.write("No credibility issues detected")

            # RED FLAGS
            st.subheader("Red Flag Words")

            if red_flags:
                for w in red_flags:
                    st.write("-", w)
            else:
                st.write("No suspicious words detected")

            # SAFETY TIPS
            tips = get_safety_tips(final_score)

            st.subheader("Safety Tips")

            for tip in tips:
                st.write("-", tip)

            # PDF DOWNLOAD
            pdf = generate_pdf(
                ml_probability,
                rule_score,
                final_score,
                reasons,
                red_flags
            )

            st.download_button(
                label="Download Report as PDF",
                data=pdf,
                file_name="job_report.pdf",
                mime="application/pdf"
            )


# =====================================================
# HISTORY
# =====================================================
elif page == "History":

    st.title("Analysis History")

    cursor.execute("SELECT * FROM job_history ORDER BY id DESC")

    rows = cursor.fetchall()

    if rows:

        history_data = []

        for r in rows:
            history_data.append({
                "ID": r[0],
                "Job Description": r[1][:120] + "...",
                "ML Score": r[2],
                "Rule Score": r[3],
                "Final Score": r[4]
            })

        df = pd.DataFrame(history_data)

        st.dataframe(df, use_container_width=True)

    else:
        st.write("No history available yet.")


# =====================================================
# ANALYTICS
# =====================================================
elif page == "Analytics":

    st.title("Analytics Dashboard")

    data1 = pd.DataFrame({
        "Category": ["Fake Jobs", "Legit Jobs", "Suspicious"],
        "Count": [35, 50, 15]
    })

    data2 = pd.DataFrame({
        "Risk Level": ["Low", "Medium", "High"],
        "Jobs": [40, 30, 30]
    })

    data3 = pd.DataFrame({
        "Platform": ["LinkedIn", "WhatsApp", "Telegram", "Other"],
        "Scams": [20, 40, 25, 15]
    })

    data4 = pd.DataFrame({
        "Year": ["2021", "2022", "2023", "2024", "2025"],
        "Scams Detected": [15, 30, 45, 60, 80]
    })

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        fig1 = px.bar(data1, x="Category", y="Count", title="Job Classification")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.pie(data2, names="Risk Level", values="Jobs", title="Risk Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        fig3 = px.bar(data3, x="Platform", y="Scams", title="Scam Platforms")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        fig4 = px.line(data4, x="Year", y="Scams Detected", title="Yearly Scam Trend")
        st.plotly_chart(fig4, use_container_width=True)


# =====================================================
# ABOUT
# =====================================================
elif page == "About":

    st.title("About")

    st.write("""
This Fake Job Detection System analyzes job descriptions using:

• Machine Learning prediction  
• Rule-based scam keyword detection  
• Company credibility analysis  
• Job category risk analysis  

The system helps job seekers identify fraudulent job postings and stay safe from online job scams.
""")


