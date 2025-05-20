import streamlit as st

st.title("Parameter Explanations")

st.markdown("Use the dropdown below to learn what each simulation input means and how it affects outcomes.")

parameter = st.selectbox(
    "Choose a parameter to explain:",
    [
        "Initial learners",
        "Program duration (months)",
        "Revenue per learner/month",
        "Major drop-off rate in incentive month",
        "Organic drop-off rate before incentive",
        "Organic drop-off rate after incentive",
        "Month of incentive offer",
        "Incentive cost per learner",
        "Retention improvement from incentive (%)",
        "% of eligible learners who redeem reward",
        "Assume redeemers stay to end of program"
    ]
)

explanations = {
    "Initial learners": "The total number of learners enrolled at the beginning of the program.",
    "Program duration (months)": "The number of months the learning program runs for.",
    "Revenue per learner/month": "The amount of money earned from each active learner per month.",
    "Major drop-off rate in incentive month": "The % of learners expected to drop out in the incentive month (e.g., Month 3), before any intervention.",
    "Organic drop-off rate before incentive": "The natural monthly dropout rate before the incentive is offered.",
    "Organic drop-off rate after incentive": "The natural monthly dropout rate after the incentive month.",
    "Month of incentive offer": "The month in the program when the incentive is introduced to improve retention.",
    "Incentive cost per learner": "The cost to the business for each learner who redeems the incentive (e.g., free month = $5).",
    "Retention improvement from incentive (%)": "How effective the incentive is at reducing drop-off. For example, a 50% improvement halves the drop rate in that month.",
    "% of eligible learners who redeem reward": "Of the learners eligible for the reward, what % actually redeem it. This impacts total incentive cost.",
    "Assume redeemers stay to end of program": "If checked, learners who redeem are assumed to complete the rest of the program without dropping out."
}

st.markdown(f"**{parameter}:** {explanations[parameter]}")
