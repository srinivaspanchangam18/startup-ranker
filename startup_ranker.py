import streamlit as st
import numpy as np

st.set_page_config(page_title="Startup Performance Evaluator", layout="centered")

# Title
st.title("🚀 Startup Performance Evaluator")

# Instructions
st.markdown("""
Enter your startup details below. The app will calculate a performance score, predict success probability, and give a success message based on your input.
""")

# Input fields
st.subheader("🔢 Input Your Startup Details")

turnover = st.number_input("Annual Turnover (₹ in Lakhs)", min_value=0.0, step=0.1)
total_funding = st.number_input("Total Funding Received (₹ in Lakhs)", min_value=0.0, step=0.1)
employees = st.number_input("Number of Employees", min_value=1, step=1)
development_stage = st.slider("Development Stage (0: None to 4: Market Launch)", 0, 4, 0)
gst_filed = st.selectbox("GST Filed?", ["Yes", "No"])
current_status = st.selectbox("Current Status", ["Active", "Inactive", "Dormant"])

# Compute status score
status_score = 1 if current_status == "Active" else (0.5 if current_status == "Dormant" else 0)

# Normalize and compute KPIs
turnover_score = min(turnover / 100, 1)  # Assuming 100L is max scale
funding_score = min(total_funding / 100, 1)  # Assuming 100L is max scale
employee_score = min(employees / 50, 1)  # Assuming 50 employees is top scale
revenue_per_employee = turnover / employees
rpe_score = min(revenue_per_employee / 5, 1)  # Assuming ₹5L per employee is max scale
gst_score = 1 if gst_filed == "Yes" else 0
stage_score = development_stage / 4  # Normalize to 0–1

# Weights (you can tweak as needed)
weights = {
    "turnover": 0.2,
    "funding": 0.2,
    "employees": 0.1,
    "rpe": 0.15,
    "gst": 0.1,
    "stage": 0.15,
    "status": 0.1,
}

# Final performance score
performance_score = (
    weights["turnover"] * turnover_score +
    weights["funding"] * funding_score +
    weights["employees"] * employee_score +
    weights["rpe"] * rpe_score +
    weights["gst"] * gst_score +
    weights["stage"] * stage_score +
    weights["status"] * status_score
) * 100  # scale to 0–100

# Estimate success probability (simplified logic)
success_probability = round((performance_score / 100), 2)

# Message logic
if performance_score >= 80:
    message = "🌟 Excellent! Your startup is very close to success."
elif performance_score >= 60:
    message = "✅ Good! You're on the right track. Keep growing!"
elif performance_score >= 40:
    message = "⚠ Moderate. Focus on key areas like revenue and market launch."
else:
    message = "🔴 Needs improvement. Revisit your business fundamentals."

# Display results
st.subheader("📊 Results")
st.metric("Performance Score", f"{performance_score:.2f} / 100")
st.metric("Success Probability", f"{success_probability * 100:.0f}%")
st.info(message)
