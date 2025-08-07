import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Load original dataset
@st.cache_data
def load_data():
    return pd.read_csv("AIC_DATA - Copied.csv")

# KPI columns and weights
kpi_cols = ['turnover', 'total_funding', 'employees', 'dev_stage_score', 'rev_per_emp', 'gst_filed']
weights = {
    'turnover': 0.20,
    'total_funding': 0.15,
    'employees': 0.10,
    'dev_stage_score': 0.10,
    'rev_per_emp': 0.15,
    'gst_filed': 0.10,
    'status_score': 0.10
}

# Scoring function (compare with original data)
def score_new_startup(new_data, existing_data):
    # Apply feature engineering to existing data
    existing_data['total_funding'] = existing_data[['external_loans', 'angel_funds', 'vc_funds', 'other_funds', 'aic_funds']].sum(axis=1)
    existing_data['dev_stage_score'] = existing_data[['proof_of_concept', 'prototype_development', 'product_development', 'field_trails', 'market_launch']].sum(axis=1)
    existing_data['status_score'] = existing_data['current_status'].map({'Active': 1, 'Graduated': 0})
    existing_data['rev_per_emp'] = existing_data['turnover'] / existing_data['employees'].replace(0, 1)

    # Keep only scoring columns
    existing_data = existing_data[kpi_cols + ['status_score']].copy()

    # Combine both datasets
    temp_data = pd.concat([existing_data, new_data[kpi_cols + ['status_score']]], ignore_index=True)

    # Normalize
    scaler = MinMaxScaler()
    temp_data[kpi_cols] = scaler.fit_transform(temp_data[kpi_cols])

    # Compute performance score
    temp_data['performance_score'] = (
        temp_data['turnover'] * weights['turnover'] +
        temp_data['total_funding'] * weights['total_funding'] +
        temp_data['employees'] * weights['employees'] +
        temp_data['dev_stage_score'] * weights['dev_stage_score'] +
        temp_data['rev_per_emp'] * weights['rev_per_emp'] +
        temp_data['gst_filed'] * weights['gst_filed'] +
        temp_data['status_score'] * weights['status_score']
    )

    # Rank all startups
    temp_data['rank'] = temp_data['performance_score'].rank(method='min', ascending=False)

    # Return the latest (new) row's score and rank
    new_score = temp_data.iloc[-1]['performance_score']
    new_rank = int(temp_data.iloc[-1]['rank'])
    total = len(temp_data)
    return new_score, new_rank, total

# Streamlit UI
st.title("🚀 Startup Performance Ranker")

# Store session results
if "results" not in st.session_state:
    st.session_state["results"] = pd.DataFrame(columns=["Startup", "Score", "Rank", "Total"])

# Input section
st.subheader("Enter Startup Details")

startup_name = st.text_input("Startup Name (e.g., S1, MyStartup)")

turnover = st.number_input("Turnover (₹ Lakhs)", min_value=0.0, step=1000.0)
external_loans = st.number_input("External Loans", min_value=0.0, step=1000.0)
angel_funds = st.number_input("Angel Funds", min_value=0.0, step=1000.0)
vc_funds = st.number_input("VC Funds", min_value=0.0, step=1000.0)
other_funds = st.number_input("Other Funds", min_value=0.0, step=1000.0)
aic_funds = st.number_input("AIC Funds", min_value=0.0, step=1000.0)
employees = st.number_input("Number of Employees", min_value=0, step=1)

proof_of_concept = st.checkbox("Proof of Concept")
prototype_development = st.checkbox("Prototype Development")
product_development = st.checkbox("Product Development")
field_trials = st.checkbox("Field Trials")
market_launch = st.checkbox("Market Launch")

gst_filed = st.selectbox("GST Filed", options=[1, 0])
status = st.selectbox("Current Status", options=["Active", "Graduated"])

# Button action
if st.button("Get Rank"):
    if startup_name.strip() == "":
        st.warning("Please enter a name for the startup.")
    else:
        # Create DataFrame for new entry
        new_data = pd.DataFrame([{
            'turnover': turnover,
            'external_loans': external_loans,
            'angel_funds': angel_funds,
            'vc_funds': vc_funds,
            'other_funds': other_funds,
            'aic_funds': aic_funds,
            'employees': employees,
            'proof_of_concept': int(proof_of_concept),
            'prototype_development': int(prototype_development),
            'product_development': int(product_development),
            'field_trails': int(field_trials),
            'market_launch': int(market_launch),
            'gst_filed': gst_filed,
            'current_status': status
        }])

        # Derived features
        new_data['total_funding'] = new_data[['external_loans', 'angel_funds', 'vc_funds', 'other_funds', 'aic_funds']].sum(axis=1)
        new_data['dev_stage_score'] = new_data[['proof_of_concept', 'prototype_development', 'product_development', 'field_trails', 'market_launch']].sum(axis=1)
        new_data['status_score'] = new_data['current_status'].map({'Active': 1, 'Graduated': 0})
        new_data['rev_per_emp'] = new_data['turnover'] / new_data['employees'].replace(0, 1)

        # Load and score
        existing_data = load_data()
        score, rank, total = score_new_startup(new_data, existing_data)

        # Save result
        st.session_state["results"] = pd.concat([
            st.session_state["results"],
            pd.DataFrame([{
                "Startup": startup_name,
                "Score": round(score, 4),
                "Rank": rank,
                "Total": total
            }])
        ], ignore_index=True)

        st.success(f"Performance Score: {score:.4f}")
        st.info(f"Ranked #{rank} out of {total} startups")

# Show past results
if not st.session_state["results"].empty:
    st.subheader("🗂 Scored Startups (This Session)")
    st.dataframe(st.session_state["results"])

    st.download_button(
        label="📥 Download Results as CSV",
        data=st.session_state["results"].to_csv(index=False).encode('utf-8'),
        file_name='startup_scores.csv',
        mime='text/csv'
    )
