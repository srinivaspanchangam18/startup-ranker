import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Load the dataset
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

# Scoring function (uses all data for better normalization)
def score_new_startup(new_data, existing_data):
    temp_data = pd.concat([existing_data.copy(), new_data], ignore_index=True)

    scaler = MinMaxScaler()
    temp_data[kpi_cols] = scaler.fit_transform(temp_data[kpi_cols])

    temp_data['performance_score'] = (
        temp_data['turnover'] * weights['turnover'] +
        temp_data['total_funding'] * weights['total_funding'] +
        temp_data['employees'] * weights['employees'] +
        temp_data['dev_stage_score'] * weights['dev_stage_score'] +
        temp_data['rev_per_emp'] * weights['rev_per_emp'] +
        temp_data['gst_filed'] * weights['gst_filed'] +
        temp_data['status_score'] * weights['status_score']
    )

    temp_data['rank'] = temp_data['performance_score'].rank(ascending=False)
    new_score = temp_data.iloc[-1]['performance_score']
    new_rank = int(temp_data.iloc[-1]['rank'])
    return new_score, new_rank, len(temp_data)

# Streamlit UI
st.title("Startup Performance Ranker")

st.markdown("Enter your startup details below:")

# User Inputs (no default values)
turnover = st.number_input("Turnover", min_value=0.0)
external_loans = st.number_input("External Loans", min_value=0.0)
angel_funds = st.number_input("Angel Funds", min_value=0.0)
vc_funds = st.number_input("VC Funds", min_value=0.0)
other_funds = st.number_input("Other Funds", min_value=0.0)
aic_funds = st.number_input("AIC Funds", min_value=0.0)
employees = st.number_input("Number of Employees", min_value=0)

proof_of_concept = st.checkbox("Proof of Concept")
prototype_development = st.checkbox("Prototype Development")
product_development = st.checkbox("Product Development")
field_trials = st.checkbox("Field Trials")
market_launch = st.checkbox("Market Launch")

gst_filed = st.selectbox("GST Filed", options=[1, 0])
status = st.selectbox("Current Status", options=["Active", "Graduated"])

# Run when button clicked
if st.button("Get Rank"):
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

    # Feature Engineering
    new_data['total_funding'] = new_data[['external_loans', 'angel_funds', 'vc_funds', 'other_funds', 'aic_funds']].sum(axis=1)
    new_data['dev_stage_score'] = new_data[['proof_of_concept', 'prototype_development', 'product_development', 'field_trails', 'market_launch']].sum(axis=1)
    new_data['status_score'] = new_data['current_status'].map({'Active': 1, 'Graduated': 0})
    new_data['rev_per_emp'] = new_data['turnover'] / new_data['employees'].replace(0, 1)

    existing_data = load_data()
    score, rank, total = score_new_startup(new_data, existing_data)

    st.success(f"Performance Score: **{score:.4f}**")
    st.info(f"Ranked **#{rank} out of {total} startups**")




