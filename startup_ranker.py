import streamlit as st
import pandas as pd
import os

# File to store results
DATA_FILE = "startup_results.csv"

# Weight configuration (total = 1.0)
weights = {
    'turnover': 0.2,
    'total_funding': 0.15,
    'employees': 0.15,
    'dev_stage_score': 0.1,
    'rev_per_emp': 0.1,
    'gst_filed': 0.1,
    'status_score': 0.1,
    'ip_score': 0.1  # IP field weight set to 0.1
}

# Maximum possible values for normalization
max_values = {
    'turnover': 1000000,       
    'total_funding': 1000000,  
    'employees': 1000,         
    'dev_stage_score': 5,      
    'rev_per_emp': 100000,     
    'gst_filed': 1,            
    'status_score': 1,         
    'ip_score': 10             
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
turnover = st.number_input("Turnover", min_value=0.0, step=0.01)
total_funding = st.number_input("Total Funding", min_value=0.0, step=0.01)
employees = st.number_input("Number of Employees", min_value=0.0, step=0.01)
rev_per_emp = st.number_input("Revenue per Employee", min_value=0.0, step=0.01)
ip_score = st.number_input("IP Score (0–10)", min_value=0.0, max_value=10.0, step=0.1)

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
        # Normalize and calculate weighted score
        score = sum([
            (turnover / max_values['turnover']) * weights['turnover'],
            (total_funding / max_values['total_funding']) * weights['total_funding'],
            (employees / max_values['employees']) * weights['employees'],
            (dev_stage_score / max_values['dev_stage_score']) * weights['dev_stage_score'],
            (rev_per_emp / max_values['rev_per_emp']) * weights['rev_per_emp'],
            (gst_filed / max_values['gst_filed']) * weights['gst_filed'],
            (status_score / max_values['status_score']) * weights['status_score'],
            (ip_score / max_values['ip_score']) * weights['ip_score']
        ])

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

        st.success(f"Performance Score: **{score:.4f}**")
        st.info(f"Ranked **#{current_rank}**")

# Show results table at the end
if not st.session_state["results"].empty:
    st.subheader("All Scored Startups")
    st.dataframe(st.session_state["results"].sort_values(by="Rank"))
