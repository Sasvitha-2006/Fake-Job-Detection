import streamlit as st
import pandas as pd
import joblib
import sqlite3
import plotly.express as px
import io
from reportlab.pdfgen import canvas

from rule_based import rule_based_score
from company_check import check_company_credibility
from job_category_risk import job_category_risk
from safety_tips import get_safety_tips

st.set_page_config(page_title="Fake Job Detection System", layout="wide")

# ---------------- DATABASE ----------------

conn = sqlite3.connect("history.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT PRIMARY KEY,
password TEXT
)
""")

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

if "analysis" not in st.session_state:
    st.session_state.analysis = None


# ---------------- LOGIN / REGISTER ----------------

if not st.session_state.logged_in:

    st.title("Fake Job Detection System")

    menu = st.selectbox("Menu", ["Login", "Register"])

    if menu == "Login":

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            cursor.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            )

            user = cursor.fetchone()

            if user:
                st.session_state.logged_in = True
                st.session_state.analysis = None
                st.success("Login successful")
                st.rerun()

            else:
                st.error("Invalid username or password")

    if menu == "Register":

        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")

        if st.button("Register"):

            cursor.execute(
                "SELECT * FROM users WHERE username=?",
                (new_user,)
            )

            if cursor.fetchone():
                st.warning("Username already exists")

            else:
                cursor.execute(
                    "INSERT INTO users VALUES (?,?)",
                    (new_user, new_pass)
                )
                conn.commit()

                st.success("Registration successful")

    st.stop()


# ---------------- LOAD MODEL ----------------

model = joblib.load("job_fraud_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")


# ---------------- SIDEBAR ----------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Menu",
    ["Job Checker", "History", "Analytics Dashboard", "About"]
)

if st.sidebar.button("Logout"):

    st.session_state.logged_in = False
    st.session_state.analysis = None
    st.rerun()


# ---------------- PDF FUNCTION ----------------

def generate_pdf(ml, rule, final):

    buffer = io.BytesIO()

    c = canvas.Canvas(buffer)

    c.drawString(100, 800, "Fake Job Detection Report")
    c.drawString(100, 760, f"ML Scam Probability: {ml:.2f}%")
    c.drawString(100, 740, f"Rule Score: {rule}")
    c.drawString(100, 720, f"Final Risk Score: {final:.2f}%")

    c.save()

    buffer.seek(0)

    return buffer


# ================= JOB CHECKER =================

if page == "Job Checker":

    st.title("Fake Job Detection Dashboard")

    job_text = st.text_area("Enter Job Description")

    if st.button("Analyze Job"):

        if job_text.strip() == "":
            st.warning("Enter job description")

        else:

            X = vectorizer.transform([job_text])
            ml_prob = model.predict_proba(X)[0][1] * 100

            rule_score, flags = rule_based_score(job_text)

            final_score = (ml_prob * 0.7) + (rule_score * 0.3)

            category, risk = job_category_risk(job_text)

            credibility, cred_score, reasons = check_company_credibility(job_text)

            cursor.execute(
                "INSERT INTO job_history(job_text,ml_score,rule_score,final_score) VALUES(?,?,?,?)",
                (job_text, ml_prob, rule_score, final_score)
            )

            conn.commit()

            st.session_state.analysis = (ml_prob, rule_score, final_score, flags, reasons, credibility)


    if st.session_state.analysis:

        ml_prob, rule_score, final_score, flags, reasons, credibility = st.session_state.analysis

        col1, col2, col3 = st.columns(3)

        col1.metric("ML Scam Probability", f"{ml_prob:.2f}%")
        col2.metric("Rule Score", rule_score)
        col3.metric("Final Risk Score", f"{final_score:.2f}%")

        st.progress(int(final_score))

        st.subheader("Company Credibility")

        st.write(credibility)

        st.subheader("Red Flag Words")

        if flags:
            for f in flags:
                st.write("-", f)
        else:
            st.write("No suspicious words detected")

        st.subheader("Reasons")

        if reasons:
            for r in reasons:
                st.write("-", r)

        tips = get_safety_tips(final_score)

        st.subheader("Safety Tips")

        for t in tips:
            st.write("-", t)

        pdf = generate_pdf(ml_prob, rule_score, final_score)

        st.download_button(
            "Download PDF Report",
            data=pdf,
            file_name="report.pdf"
        )


# ================= HISTORY =================

elif page == "History":

    st.title("Job Analysis History")

    cursor.execute("SELECT * FROM job_history ORDER BY id DESC")

    rows = cursor.fetchall()

    if rows:

        df = pd.DataFrame(
            rows,
            columns=["ID", "Job Text", "ML Score", "Rule Score", "Final Score"]
        )

        st.dataframe(df)

    else:
        st.write("No history yet")


# ================= ANALYTICS =================

elif page == "Analytics Dashboard":

    st.title("Analytics Dashboard")

    cursor.execute("SELECT final_score FROM job_history")

    rows = cursor.fetchall()

    if rows:

        df = pd.DataFrame(rows, columns=["Risk"])

        low = len(df[df["Risk"] < 40])
        medium = len(df[(df["Risk"] >= 40) & (df["Risk"] < 70)])
        high = len(df[df["Risk"] >= 70])

        risk_df = pd.DataFrame({
            "Risk Level": ["Low", "Medium", "High"],
            "Jobs": [low, medium, high]
        })

        fig1 = px.pie(risk_df, names="Risk Level", values="Jobs", title="Risk Distribution")
        fig2 = px.bar(risk_df, x="Risk Level", y="Jobs", title="Risk Categories")
        fig3 = px.histogram(df, x="Risk", nbins=10, title="Risk Score Distribution")
        fig4 = px.box(df, y="Risk", title="Risk Score Spread")

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.plotly_chart(fig4, use_container_width=True)

    else:
        st.warning("No data available for analytics")


# ================= ABOUT =================

elif page == "About":

    st.title("About")

    st.write("""
This Fake Job Detection System helps identify fraudulent job postings using:

• Machine Learning prediction  
• Rule-based scam detection  
• Company credibility analysis  
• Risk score evaluation  

The system helps job seekers avoid online job scams.
""")