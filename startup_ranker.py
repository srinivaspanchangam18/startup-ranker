import streamlit as st
import pandas as pd
import os

# File to store results
DATA_FILE = "startup_results.csv"

# Weight configuration
weights = {
    'turnover': 0.20,
    'total_funding': 0.20,
    'employees': 0.10,
    'ip_filed': 0.10,
    'dev_stage_score': 0.10,
    'rev_per_emp': 0.10,
    'gst_filed': 0.10,
    'status_score': 0.10
}

# Maximum possible values for normalization
max_values = {
    'turnover': 1000000,       # Example: max turnover is 1M
    'total_funding': 1000000,  # Example: max funding is 1M
    'employees': 1000,         # Example: max 1000 employees
    'dev_stage_score': 5,      # 5 stages max
    'ip_filed': 100,           # Example: max IP filed score is 100
    'rev_per_emp': 100000,     # Example: max revenue per employee is 100k
    'gst_filed': 1,            # 1 or 0
    'status_score': 1          # 1 or 0
}

# Load existing results if file exists
if "results" not in st.session_state:
    if os.path.exists(DATA_FILE):
        st.session_state["results"] = pd.read_csv(DATA_FILE)
    else:
        st.session_state["results"] = pd.DataFrame(columns=["Startup", "Performance Score", "Rank"])

st.title("Startup Ranker")

# Input fields
startup_name = st.text_input("Enter Startup Name")
turnover = st.number_input("Turnover", min_value=0, step=100)
total_funding = st.number_input("Total Funding", min_value=0, step=100)
ip_filed = st.number_input("IP Filed", min_value=0, max_value=max_values['ip_filed'], step=1)
employees = st.number_input("Number of Employees", min_value=0, step=1)
rev_per_emp = st.number_input("Revenue per Employee", min_value=0, step=100)

# Development stage checkboxes
st.subheader("Development Stage")
proof_of_concept = st.checkbox("Proof of Concept")
prototype_development = st.checkbox("Prototype Development")
product_development = st.checkbox("Product Development")
field_trials = st.checkbox("Field Trials")
market_launch = st.checkbox("Market Launch")

# Calculate development stage score
dev_stage_score = (
    int(proof_of_concept) +
    int(prototype_development) +
    int(product_development) +
    int(field_trials) +
    int(market_launch)
)

gst_filed = st.selectbox("GST Filed", options=[1, 0])

# Status score (Active = 1, Inactive = 0)
status_choice = st.selectbox("Status", options=["Active", "Inactive"])
status_score = 1 if status_choice == "Active" else 0

if st.button("Calculate Rank"):
    if startup_name.strip() == "":
        st.error("Please enter a startup name.")
    else:
        # Normalize each metric before weighting
        score = (
            (turnover / max_values['turnover']) * weights['turnover'] +
            (total_funding / max_values['total_funding']) * weights['total_funding'] +
            (employees / max_values['employees']) * weights['employees'] +
            (dev_stage_score / max_values['dev_stage_score']) * weights['dev_stage_score'] +
            (ip_filed / max_values['ip_filed']) * weights['ip_filed'] +
            (rev_per_emp / max_values['rev_per_emp']) * weights['rev_per_emp'] +
            (gst_filed / max_values['gst_filed']) * weights['gst_filed'] +
            (status_score / max_values['status_score']) * weights['status_score']
        )

        # Add startup and score to session data
        st.session_state["results"] = pd.concat([
            st.session_state["results"],
            pd.DataFrame([{"Startup": startup_name, "Performance Score": round(score, 4)}])
        ], ignore_index=True)

        # Rank startups (highest score = rank 1)
        st.session_state["results"]["Rank"] = st.session_state["results"]["Performance Score"].rank(
            method="dense", ascending=False
        ).astype(int)

        # Save to CSV
        st.session_state["results"].to_csv(DATA_FILE, index=False)

        # Show current startup rank
        current_rank = st.session_state["results"].loc[
            st.session_state["results"]["Startup"] == startup_name, "Rank"
        ].iloc[-1]

        st.success(f"Performance Score: {score:.4f}")
        st.info(f"Ranked #{current_rank}")

# Show results table at the end
if not st.session_state["results"].empty:
    st.subheader("All Scored Startups")
    st.dataframe(st.session_state["results"].sort_values(by="Rank"))
