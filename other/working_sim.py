# rewards_retention_model.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(page_title="Retention Incentive Simulator", layout="wide")

# --- SIDEBAR: Parameters ---
st.sidebar.header("Simulation Settings")

# --- PARAMETERS ---
redeemers_stay_full = st.sidebar.checkbox("Assume redeemers stay to end of program", True)
initial_learners = st.sidebar.number_input("Initial learners", 100, 10000, 1000, 100)
duration_months = st.sidebar.slider("Program duration (months)", 4, 12, 8)
revenue_per_month = st.sidebar.number_input("Revenue per learner/month ($)", 1.0, 10.0, 5.0)
incentive_cost = st.sidebar.number_input("Incentive cost per learner ($)", 0.0, 10.0, 5.0)
incentive_effect = st.sidebar.slider("Retention improvement from incentive (%)", 0, 100, 50)
redeem_rate = st.sidebar.slider("% of eligible learners who redeem reward", 0, 100, 70)
drop_off_rate = st.sidebar.slider("Major drop-off rate in incentive month (%)", 5, 50, 25)
organic_drop_pre = st.sidebar.slider("Organic drop-off rate before incentive (%)", 0, 20, 5)
organic_drop_post = st.sidebar.slider("Organic drop-off rate after incentive (%)", 0, 20, 10)
drop_month = st.sidebar.slider("Month of incentive offer", 2, duration_months - 1, 3)

# --- DROPOFF SETUP ---
monthly_drop = ([organic_drop_pre / 100] 
                * (drop_month - 1) 
                + [drop_off_rate / 100] 
                + [organic_drop_post / 100] 
                * (duration_months - drop_month - 1))

# --- BASELINE SCENARIO ---
learners = [initial_learners]
for i in range(1, duration_months):
    drop = monthly_drop[i - 1]
    learners.append(learners[-1] * (1 - drop))
baseline_df = pd.DataFrame({"Month": range(1, duration_months + 1), "Learners": learners})

# --- INCENTIVE SCENARIO ---
learners_incentive = [initial_learners]
for i in range(1, duration_months):
    drop = (monthly_drop[i - 1] 
            * (1 - incentive_effect / 100) if i == drop_month - 1 else monthly_drop[i - 1])
    next_count = learners_incentive[-1] * (1 - drop)
    if redeemers_stay_full and i == drop_month:
        retained = (learners_incentive[-1] 
                    * monthly_drop[i - 1] 
                    * (incentive_effect / 100) 
                    * (redeem_rate / 100))
        next_count += retained
    learners_incentive.append(next_count)
incentive_df = pd.DataFrame({"Month": range(1, duration_months + 1), "Learners": learners_incentive})

# --- Revenue & Summary ---
baseline_revenue = np.sum(np.array(learners) * revenue_per_month)
incentive_revenue = np.sum(np.array(learners_incentive) * revenue_per_month)
actual_redeemers = learners_incentive[drop_month - 1] * (redeem_rate / 100)
total_cost = actual_redeemers * incentive_cost
net_revenue = incentive_revenue - total_cost
retention_gain = learners_incentive[-1] - learners[-1]
retention_pct = (retention_gain / learners[-1]) * 100 if learners[-1] > 0 else 0
break_even = (total_cost 
              / (revenue_per_month * (duration_months - drop_month)) 
              if (duration_months - drop_month) > 0 else 0)

# --- EXECUTIVE SUMMARY ---
st.title("Retention Incentive Simulator")
st.subheader("Executive Summary")
st.dataframe(pd.DataFrame({
    "Scenario": ["Baseline", "Incentive"],
    "Total Revenue": [f"${baseline_revenue:,.0f}", f"${incentive_revenue:,.0f}"],
    "Incentive Cost": ["$0", f"${total_cost:,.0f}"],
    "Net Revenue": [f"${baseline_revenue:,.0f}", f"${net_revenue:,.0f}"],
    "Retention Gain": ["-", f"{retention_gain:.0f} learners"],
    "Retention Gain (%)": ["-", f"{retention_pct:.1f}%"],
    "Break-Even Learners Needed": ["-", f"{break_even:.0f}"]
}), use_container_width=True)

# --- VISUALIZATIONS ---
st.subheader("Monthly Revenue Comparison")
monthly_rev_baseline = [l * revenue_per_month for l in learners]
monthly_rev_incentive = [l * revenue_per_month for l in learners_incentive]
bar_fig = go.Figure()
bar_fig.add_bar(x=list(range(1, duration_months + 1)), 
                y=monthly_rev_baseline, name="Baseline Revenue")
bar_fig.add_bar(x=list(range(1, duration_months + 1)), 
                y=monthly_rev_incentive, name="Incentive Revenue")
bar_fig.update_layout(barmode="group", 
                      xaxis_title="Month", 
                      yaxis_title="Revenue ($)", height=400)
st.plotly_chart(bar_fig)

st.subheader("Learner Retention Curve")
fig = go.Figure()
fig.add_trace(go.Scatter(x=baseline_df["Month"], 
                         y=baseline_df["Learners"], 
                         mode="lines+markers", name="Baseline"))
fig.add_trace(go.Scatter(x=incentive_df["Month"], 
                         y=incentive_df["Learners"], 
                         mode="lines+markers", name="Incentive"))
fig.update_layout(title="Learner Retention Over Time", 
                  xaxis_title="Month", yaxis_title="Active Learners", height=400)
st.plotly_chart(fig)

# --- Assumptions ---
st.markdown("""
### Assumptions
- Incentive effectiveness reduces drop-off rate in the designated month.
- Only a portion of at-risk learners redeem rewards and are retained.
- Retained learners can be assumed to stay until program end (toggle).
- Baseline scenario models organic drop-off before and after incentive month.
""")
