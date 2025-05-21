import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Retention Incentive Simulator", layout="wide")

st.title("Retention Incentive Simulator")
st.markdown("""
This app models learner retention across baseline and incentive scenarios,
allowing you to estimate financial impact and identify the optimal incentive strategy.
""")

# Sidebar Inputs
st.sidebar.subheader("GLOBAL SETTINGS")
redeemers_stay_full = st.sidebar.checkbox("Assume redeemers stay to end of program", value=True)
revenue_per_month = st.sidebar.number_input("Revenue per learner/month ($)", 0.0, 100.0, value=5.0)
incentive_cost = st.sidebar.number_input("Incentive cost per learner ($)", 0.0, 100.0, value=5.0)
initial_learners = st.sidebar.number_input("Initial learners", 100, 10000, value=1000)
duration_months = st.sidebar.slider("Program duration (months)", 4, 12, value=8)
drop_month = st.sidebar.slider("Month of incentive offer", 2, duration_months - 1, 3)
drop_off_rate = st.sidebar.slider("Major drop-off rate in incentive month (%)", 0, 100, 30)
organic_drop_pre = st.sidebar.slider("Organic drop-off rate before incentive (%)", 0, 100, 0)
organic_drop_post = st.sidebar.slider("Organic drop-off rate after incentive (%)", 0, 100, 0)

st.sidebar.subheader("SCENARIO SETTINGS")
st.sidebar.subheader("Scenario 1. Intervention, no effect")
incentive_effect_1 = st.sidebar.slider("Retention improvement from incentive (%)", 0, 100, 0)
redeem_rate_1 = st.sidebar.slider("% of eligible learners who redeem reward", 0, 100, 50)


st.sidebar.subheader("Scenario 2. Intervention, improved retention")
incentive_effect_2 = (st.sidebar.slider("Retention improvement from incentive (%)", 0, 100, 100))
redeem_rate_2 = st.sidebar.slider("% of eligible learners who redeem reward", 0, 100, 100)

# Dropoff Setup
monthly_drop = ([organic_drop_pre / 100] 
                * (drop_month - 1) 
                + [drop_off_rate / 100] 
                + [organic_drop_post / 100] 
                * (duration_months - drop_month - 1))

# Scenario Simulations
def simulate_learners(effect, rate):
    learners = [initial_learners]
    for i in range(1, duration_months):
        drop = monthly_drop[i - 1] * (1 - effect / 100) if i == drop_month - 1 else monthly_drop[i - 1]
        retained = learners[-1] * (1 - drop)
        if redeemers_stay_full and i == drop_month:
            retained += learners[-1] * monthly_drop[i - 1] * (effect / 100) * (rate / 100)
        learners.append(retained)
    return learners

learners_base = simulate_learners(0, 0)
learners_s1 = simulate_learners(incentive_effect_1, redeem_rate_1)
learners_s2 = simulate_learners(incentive_effect_2, redeem_rate_2)

# -----------------------------
# Financial Calculations
# -----------------------------
def compute_summary(name, learners, effect, rate):
    revenue = sum([x * revenue_per_month for x in learners])
    redeemers = learners[drop_month - 1] * rate / 100
    cost = redeemers * incentive_cost if effect > 0 else 0
    net = revenue - cost
    gain = learners[-1] - learners_base[-1]
    pct_gain = (gain / learners_base[-1]) * 100 if learners_base[-1] > 0 else 0
    break_even = cost / (revenue_per_month * (duration_months - drop_month)) if (duration_months - drop_month) > 0 else 0
    return {
        "Scenario": name,
        "Total Revenue": f"${revenue:,.0f}",
        "Incentive Cost": f"${cost:,.0f}",
        "Net Revenue": f"${net:,.0f}",
        "Retention Gain": f"{gain:.0f} learners",
        "Retention Gain (%)": f"{pct_gain:.1f}%",
        "Break-Even Learners Needed": f"{break_even:.0f}"
    }

summary = pd.DataFrame([
    compute_summary("Baseline", learners_base, 0, 0),
    compute_summary("Scenario 1", learners_s1, incentive_effect_1, redeem_rate_1),
    compute_summary("Scenario 2", learners_s2, incentive_effect_2, redeem_rate_2)
])

# st.subheader("Executive Summary")
# st.dataframe(summary, use_container_width=True)

# -----------------------------
# Executive Recommendation
# -----------------------------
summary_clean = summary.copy()
summary_clean["Total Revenue ($)"] = summary_clean["Total Revenue"].replace(r'[$,]', '', regex=True).astype(float)
summary_clean["Net Revenue ($)"] = summary_clean["Net Revenue"].replace(r'[$,]', '', regex=True).astype(float)
summary_clean["Incentive Cost ($)"] = summary_clean["Incentive Cost"].replace(r'[$,]', '', regex=True).astype(float)

# Calculate actual redeemers regardless of incentive effect
learners_at_s1_drop = learners_s1[drop_month - 1]
learners_at_s2_drop = learners_s2[drop_month - 1]
cost_s1 = learners_at_s1_drop * (redeem_rate_1 / 100) * incentive_cost
cost_s2 = learners_at_s2_drop * (redeem_rate_2 / 100) * incentive_cost

# Define liability (unrealized value still owed post-redemption)
liability_s1 = cost_s1 if incentive_effect_1 == 0 else 0
liability_s2 = cost_s2 if incentive_effect_2 == 0 else 0

# Update cost, liability, and recompute net revenue
summary_clean.loc[summary_clean["Scenario"] == "Scenario 1", "Incentive Cost ($)"] = cost_s1
summary_clean.loc[summary_clean["Scenario"] == "Scenario 2", "Incentive Cost ($)"] = cost_s2
summary_clean.loc[summary_clean["Scenario"] == "Scenario 1", "Liability Incentive ($)"] = liability_s1
summary_clean.loc[summary_clean["Scenario"] == "Scenario 2", "Liability Incentive ($)"] = liability_s2
summary_clean.loc[summary_clean["Scenario"] == "Baseline", "Liability Incentive ($)"] = 0

summary_clean["Incentive Cost"] = summary_clean["Incentive Cost ($)"].apply(lambda x: f"${x:,.0f}")
summary_clean["Net Revenue ($)"] = summary_clean["Total Revenue ($)"] - summary_clean["Incentive Cost ($)"]
summary_clean["Net Revenue"] = summary_clean["Net Revenue ($)"].apply(lambda x: f"${x:,.0f}")
summary_clean["Liability Incentive"] = summary_clean["Liability Incentive ($)"].apply(lambda x: f"${x:,.0f}")

# Reorder columns for display
columns_order = [
    "Scenario", "Total Revenue", "Incentive Cost", "Net Revenue",
    "Retention Gain", "Retention Gain (%)", "Break-Even Learners Needed", "Liability Incentive"
]
st.subheader("Executive Summary")
st.dataframe(summary_clean[columns_order], use_container_width=True)

# Sort and recommend based on updated net revenue
best_row = summary_clean.iloc[1:].sort_values("Net Revenue ($)", ascending=False).iloc[0]
worst_row = summary_clean.iloc[1:].sort_values("Net Revenue ($)", ascending=True).iloc[0]
message = (
    f"\n📈 **Recommendation:** Adopt the **{best_row['Scenario']}** – it delivers the highest net revenue of "
    f"**{best_row['Net Revenue']}**, with a retention uplift of **{best_row['Retention Gain (%)']}**. "
    f"This requires retaining at least **{best_row['Break-Even Learners Needed']}** additional learners to break even."
    f"\n\n⚖️ Compared to **{worst_row['Scenario']}**, which yields only **{worst_row['Net Revenue']}** net revenue and "
    f"a lower retention impact, the recommended approach demonstrates a more cost-effective incentive outcome."
)
st.success(message)


# -----------------------------
# Financial Impact Bar Chart
# -----------------------------
st.subheader("Financial Impact by Scenario")

# Compute monthly revenue and liability arrays
monthly_rev_base = [x * revenue_per_month for x in learners_base]
monthly_rev_s1 = [x * revenue_per_month for x in learners_s1]
monthly_rev_s2 = [x * revenue_per_month for x in learners_s2]

monthly_liab_s1 = [0] * duration_months
monthly_liab_s2 = [0] * duration_months
monthly_liab_s1[drop_month - 1] = learners_s1[drop_month - 1] * (redeem_rate_1 / 100) * incentive_cost
monthly_liab_s2[drop_month - 1] = learners_s2[drop_month - 1] * (redeem_rate_2 / 100) * incentive_cost

# Calculate scenario totals
rev_base = sum(monthly_rev_base)
rev_s1 = sum(monthly_rev_s1)
rev_s2 = sum(monthly_rev_s2)
cost_s1 = monthly_liab_s1[drop_month - 1]
cost_s2 = monthly_liab_s2[drop_month - 1]
net_s1 = rev_s1 - cost_s1
net_s2 = rev_s2 - cost_s2

fin_fig = go.Figure()
fin_fig.add_bar(x=["Baseline", "Scenario 1", "Scenario 2"], y=[rev_base, rev_s1, rev_s2], name="Total Revenue", marker_color="#6baed6")
fin_fig.add_bar(x=["Baseline", "Scenario 1", "Scenario 2"], y=[0, cost_s1, cost_s2], name="Incentive Cost", marker_color="#fc9272")
fin_fig.add_bar(x=["Baseline", "Scenario 1", "Scenario 2"], y=[rev_base, net_s1, net_s2], name="Net Revenue", marker_color="#74c476")

# Add horizontal line for Scenario 2 Net Revenue
fin_fig.add_shape(
    type="line",
    xref="paper",
    yref="y",
    x0=0,
    x1=1,
    y0=net_s2,
    y1=net_s2,
    line=dict(color="#74c476", width=2, dash="dash")
)

fin_fig.update_layout(
    barmode="group",
    xaxis_title="Scenario",
    yaxis_title="USD ($)",
    height=400
)
st.plotly_chart(fin_fig, use_container_width=True)


# -----------------------------
# Learner Retention Comparison
# -----------------------------
st.subheader("Learner Retention Over Time")
months = list(range(1, duration_months + 1))
fig = go.Figure()
fig.add_trace(go.Scatter(x=months, y=learners_base, name="Baseline", line=dict(width=3)))
fig.add_trace(go.Scatter(x=months, y=learners_s1, name="Scenario 1", line=dict(width=3, dash="dot")))
fig.add_trace(go.Scatter(x=months, y=learners_s2, name="Scenario 2", line=dict(width=3, dash="dash")))
fig.update_layout(xaxis_title="Month", yaxis_title="Active Learners")
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Monthly Revenue and Liability
# -----------------------------
st.subheader("Monthly Revenue and Incentive Liability")
monthly_rev_base = [x * revenue_per_month for x in learners_base]
monthly_rev_s1 = [x * revenue_per_month for x in learners_s1]
monthly_rev_s2 = [x * revenue_per_month for x in learners_s2]

monthly_liab_s1 = [0] * duration_months
monthly_liab_s2 = [0] * duration_months
monthly_liab_s1[drop_month - 1] = learners_s1[drop_month - 1] * (redeem_rate_1 / 100) * incentive_cost
monthly_liab_s2[drop_month - 1] = learners_s2[drop_month - 1] * (redeem_rate_2 / 100) * incentive_cost

bar_fig = go.Figure()
bar_fig.add_bar(x=months, y=monthly_rev_base, name="Baseline Revenue", marker_color="#6baed6")
bar_fig.add_bar(x=months, y=monthly_rev_s1, name="Scenario 1 Revenue", marker_color="#9ecae1")
bar_fig.add_bar(x=months, y=monthly_rev_s2, name="Scenario 2 Revenue", marker_color="#74c476")
bar_fig.add_bar(x=months, y=monthly_liab_s1, name="Scenario 1 Liability", marker_color="#fcae91")
bar_fig.add_bar(x=months, y=monthly_liab_s2, name="Scenario 2 Liability", marker_color="#fc9272")
bar_fig.update_layout(barmode="group", xaxis_title="Month", yaxis_title="USD ($)", height=400)
st.plotly_chart(bar_fig)

# -----------------------------
# Assumptions & How to Use
# -----------------------------
st.subheader("Assumptions")
st.markdown("""
- Learners drop off organically before and after the incentive month.
- Drop-off rate in the incentive month is reduced by the specified effectiveness %.
- Only a % of learners who would have dropped off are retained via the incentive.
- Retained redeemers are assumed to stay till the end if the checkbox is enabled.
- No additional drop-off is applied to redeemers once retained.
""")

st.subheader("How to Use")
st.markdown("""
- Adjust parameters in the sidebar.
- Use the graphs and executive summary to compare scenarios and inform strategy.
""")