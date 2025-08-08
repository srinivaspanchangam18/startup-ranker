import streamlit as st
import pandas as pd
import os

# File to store results
DATA_FILE = "startup_results.csv"

# Weight configuration
weights = {
    'turnover': 0.2,
    'total_funding': 0.2,
    'employees': 0.15,
    'dev_stage_score': 0.15,
    'rev_per_emp': 0.1,
    'gst_filed': 0.1,
    'status_score': 0.1
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
dev_stage_score = st.number_input("Development Stage Score", min_value=0.0, step=0.01)
rev_per_emp = st.number_input("Revenue per Employee", min_value=0.0, step=0.01)
gst_filed = st.number_input("GST Filed (1 if yes, 0 if no)", min_value=0.0, step=0.01)
status_score = st.number_input("Status Score", min_value=0.0, step=0.01)

if st.button("Calculate Rank"):
    if startup_name.strip() == "":
        st.error("Please enter a startup name.")
    else:
        # Calculate performance score
        score = (
            turnover * weights['turnover'] +
            total_funding * weights['total_funding'] +
            employees * weights['employees'] +
            dev_stage_score * weights['dev_stage_score'] +
            rev_per_emp * weights['rev_per_emp'] +
            gst_filed * weights['gst_filed'] +
            status_score * weights['status_score']
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

        st.success(f"Performance Score: **{score:.4f}**")
        st.info(f"Ranked **#{current_rank}**")

# Show results table at the end
if not st.session_state["results"].empty:
    st.subheader("All Scored Startups")
    st.dataframe(st.session_state["results"].sort_values(by="Rank"))
