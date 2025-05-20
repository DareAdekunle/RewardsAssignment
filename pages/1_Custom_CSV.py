import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Custom CSV Retention Scenario", layout="wide")

st.title("Custom CSV Retention Scenario")
st.markdown("""
Upload a custom CSV with two columns:
- **Month** (1 to N)
- **Drop-off Rate** (as a percentage)

This page assumes you want full control over when drop-offs occur.
""")

# --- SIDEBAR PARAMETERS ---
st.sidebar.header("Simulation Settings")
initial_learners = st.sidebar.number_input("Initial learners", 1000, 1000000, 1000, 1000)
duration_months = st.sidebar.slider("Program duration (months)", 4, 12, 8)
revenue_per_month = st.sidebar.number_input("Revenue per learner/month ($)", 1.0, 10.0, 5.0)
incentive_cost = st.sidebar.number_input("Incentive cost per learner ($)", 0.0, 10.0, 5.0)
redeemers_stay_full = st.sidebar.checkbox("Assume redeemers stay to end of program", True)

st.sidebar.subheader("Scenario 1: No Effect")
incentive_effect_1 = st.sidebar.slider("Retention improvement (%) - Scenario 1", 0, 100, 0)
redeem_rate_1 = st.sidebar.slider("Redeem rate (%) - Scenario 1", 0, 100, 50)

st.sidebar.subheader("Scenario 2: Improved Retention")
incentive_effect_2 = st.sidebar.slider("Retention improvement (%) - Scenario 2", 0, 100, 100)
redeem_rate_2 = st.sidebar.slider("Redeem rate (%) - Scenario 2", 0, 100, 70)

dropoff_file = st.sidebar.file_uploader("Upload CSV with Drop-off Rates", type=["csv"], key="custom_csv_upload")

if dropoff_file is not None:
    months_df = pd.DataFrame({"Month": list(range(1, duration_months + 1))})
    csv_df = pd.read_csv(dropoff_file).iloc[:, :2]
    csv_df.columns = ["Month", "Drop-off Rate (%)"]
    csv_df["Month"] = pd.to_numeric(csv_df["Month"], errors='coerce').astype(pd.Int64Dtype())
    csv_df["Drop-off Rate (%)"] = pd.to_numeric(csv_df["Drop-off Rate (%)"], errors='coerce').fillna(0.0)
    csv_df = csv_df.dropna(subset=["Month"]).astype({"Month": int})

    merged_df = pd.merge(months_df, csv_df, how="left", on="Month")
    merged_df["Drop-off Rate (%)"] = merged_df["Drop-off Rate (%)"].fillna(0.0)
    st.subheader("Drop-off Schedule by Month")
    st.dataframe(merged_df, use_container_width=True)

    drop_rates = merged_df["Drop-off Rate (%)"] / 100

    def simulate_scenario(effect, rate):
        learners = [initial_learners]
        for i in range(1, duration_months):
            prev = learners[-1]
            drop = drop_rates.iloc[i - 1]
            retained = 0
            if drop > 0 and redeemers_stay_full:
                redeemed = prev * drop * (rate / 100)
                retained = redeemed * (effect / 100)
            learners.append(prev * (1 - drop) + retained)
        return learners

    baseline = simulate_scenario(0, 0)
    incentive_s1 = simulate_scenario(incentive_effect_1, redeem_rate_1)
    incentive_s2 = simulate_scenario(incentive_effect_2, redeem_rate_2)

    retention_df = pd.DataFrame({
        "Month": range(1, duration_months + 1),
        "Baseline": baseline,
        "Scenario 1": incentive_s1,
        "Scenario 2": incentive_s2
    })

    def calc_financials(learners, redeem_rate, effect):
        revenue = [x * revenue_per_month for x in learners]
        cost = []
        for i in range(duration_months):
            drop = drop_rates.iloc[i]
            if drop > 0:
                redeemers = learners[i] * drop * (redeem_rate / 100)
                retained = redeemers * (effect / 100)
                cost.append(redeemers * incentive_cost if effect == 0 else retained * incentive_cost)
            else:
                cost.append(0)
        return revenue, cost

    rev_base, cost_base = calc_financials(baseline, 0, 0)
    rev_s1, cost_s1 = calc_financials(incentive_s1, redeem_rate_1, incentive_effect_1)
    rev_s2, cost_s2 = calc_financials(incentive_s2, redeem_rate_2, incentive_effect_2)

    # --- EXECUTIVE SUMMARY ---
    total_revenue_base = sum(rev_base)
    total_revenue_s1 = sum(rev_s1)
    total_revenue_s2 = sum(rev_s2)
    total_cost_s1 = sum(cost_s1)
    total_cost_s2 = sum(cost_s2)
    net_revenue_s1 = total_revenue_s1 - total_cost_s1
    net_revenue_s2 = total_revenue_s2 - total_cost_s2

    gain_s1 = incentive_s1[-1] - baseline[-1]
    gain_s2 = incentive_s2[-1] - baseline[-1]
    pct_gain_s1 = (gain_s1 / baseline[-1]) * 100 if baseline[-1] > 0 else 0
    pct_gain_s2 = (gain_s2 / baseline[-1]) * 100 if baseline[-1] > 0 else 0
    break_even_s1 = total_cost_s1 / (revenue_per_month * (duration_months - 1)) if duration_months > 1 else 0
    break_even_s2 = total_cost_s2 / (revenue_per_month * (duration_months - 1)) if duration_months > 1 else 0

    summary_df = pd.DataFrame([
        {
            "Scenario": "Baseline",
            "Total Revenue": f"${total_revenue_base:,.2f}",
            "Incentive Cost": "$0",
            "Net Revenue": f"${total_revenue_base:,.2f}",
            "Retention Gain": "-",
            "Retention Gain (%)": "-",
            "Break-Even Learners Needed": "-"
        },
        {
            "Scenario": "Scenario 1",
            "Total Revenue": f"${total_revenue_s1:,.2f}",
            "Incentive Cost": f"${total_cost_s1:,.2f}",
            "Net Revenue": f"${net_revenue_s1:,.2f}",
            "Retention Gain": f"{gain_s1:.0f} learners",
            "Retention Gain (%)": f"{pct_gain_s1:.1f}%",
            "Break-Even Learners Needed": f"{break_even_s1:.0f}"
        },
        {
            "Scenario": "Scenario 2",
            "Total Revenue": f"${total_revenue_s2:,.2f}",
            "Incentive Cost": f"${total_cost_s2:,.2f}",
            "Net Revenue": f"${net_revenue_s2:,.2f}",
            "Retention Gain": f"{gain_s2:.0f} learners",
            "Retention Gain (%)": f"{pct_gain_s2:.1f}%",
            "Break-Even Learners Needed": f"{break_even_s2:.0f}"
        }
    ])
    st.subheader("Executive Summary")
    st.dataframe(summary_df, use_container_width=True)

    best_row = summary_df.iloc[1:].copy()
    best_row["Net Revenue ($)"] = best_row["Net Revenue"].replace("[$,]", "", regex=True).astype(float)
    best = best_row.sort_values("Net Revenue ($)", ascending=False).iloc[0]
    worst = best_row.sort_values("Net Revenue ($)", ascending=True).iloc[0]

    message = (
        f"\n📈 **Recommendation:** Adopt the **{best['Scenario']}** – it delivers the highest net revenue of "
        f"**{best['Net Revenue']}**, with a retention uplift of **{best['Retention Gain (%)']}**. "
        f"This requires retaining at least **{best['Break-Even Learners Needed']}** additional learners to break even."
        f"\n\n⚖️ Compared to **{worst['Scenario']}**, which yields only **{worst['Net Revenue']}**, the recommended option "
        f"is more cost-effective and delivers greater impact."
    )
    st.success(message)

    # --- FINANCIAL IMPACT BAR CHART ---
    st.subheader("Financial Impact by Scenario")
    fin_fig = go.Figure()
    fin_fig.add_bar(x=["Baseline", "Scenario 1", "Scenario 2"],
                    y=[total_revenue_base, total_revenue_s1, total_revenue_s2],
                    name="Total Revenue", marker_color="#6baed6")
    fin_fig.add_bar(x=["Baseline", "Scenario 1", "Scenario 2"],
                    y=[0, total_cost_s1, total_cost_s2],
                    name="Incentive Cost", marker_color="#fc9272")
    fin_fig.add_bar(x=["Baseline", "Scenario 1", "Scenario 2"],
                    y=[total_revenue_base, net_revenue_s1, net_revenue_s2],
                    name="Net Revenue", marker_color="#74c476")
    fin_fig.update_layout(barmode="group", xaxis_title="Scenario", yaxis_title="USD ($)", height=400)
    st.plotly_chart(fin_fig, use_container_width=True)

    # --- RETENTION CURVE ---
    st.subheader("Learner Retention Over Time")
    fig_ret = go.Figure()
    fig_ret.add_trace(go.Scatter(x=retention_df["Month"], y=retention_df["Baseline"], mode='lines+markers', name='Baseline', line=dict(color="#6baed6", width=3)))
    fig_ret.add_trace(go.Scatter(x=retention_df["Month"], y=retention_df["Scenario 1"], mode='lines+markers', name='Scenario 1', line=dict(color="#fc9272", width=3, dash="dot")))
    fig_ret.add_trace(go.Scatter(x=retention_df["Month"], y=retention_df["Scenario 2"], mode='lines+markers', name='Scenario 2', line=dict(color="#74c476", width=3, dash="dash")))
    fig_ret.update_layout(title="Retention Curve", xaxis_title="Month", yaxis_title="Active Learners", height=400)
    st.plotly_chart(fig_ret)

    # --- MONTHLY REVENUE & INCENTIVE LIABILITY ---
    st.subheader("Monthly Revenue and Incentive Liability")
    fig_bar = go.Figure()
    fig_bar.add_bar(x=retention_df["Month"], y=rev_base, name='Baseline Revenue', marker_color="#6baed6")
    fig_bar.add_bar(x=retention_df["Month"], y=rev_s1, name='Scenario 1 Revenue', marker_color="#fc9272")
    fig_bar.add_bar(x=retention_df["Month"], y=rev_s2, name='Scenario 2 Revenue', marker_color="#74c476")
    fig_bar.add_bar(x=retention_df["Month"], y=cost_s1, name='Scenario 1 Liability', marker_color="#fcbba1")
    fig_bar.add_bar(x=retention_df["Month"], y=cost_s2, name='Scenario 2 Liability', marker_color="#a1d99b")
    fig_bar.update_layout(barmode='group', title="Revenue & Incentive Cost per Month", xaxis_title="Month", yaxis_title="Amount ($)", height=400)
    st.plotly_chart(fig_bar)

else:
    st.info("Upload a CSV to simulate retention and incentives.")
