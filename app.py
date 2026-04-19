import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Smart Grid Dispatch System", layout="wide")

st.title("⚡ Smart Grid Dispatch & Monitoring System")

# ---------------- INPUT ---------------- #
load = st.slider("Load Demand (MW)", 50, 500, 200)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Generator 1")
    P1_min = st.number_input("Min Limit G1", value=50.0)
    P1_max = st.number_input("Max Limit G1", value=200.0)
    a1 = st.number_input("Cost a1", value=0.02)
    b1 = st.number_input("Cost b1", value=10.0)

with col2:
    st.subheader("Generator 2")
    P2_min = st.number_input("Min Limit G2", value=50.0)
    P2_max = st.number_input("Max Limit G2", value=200.0)
    a2 = st.number_input("Cost a2", value=0.04)
    b2 = st.number_input("Cost b2", value=8.0)

# ---------------- CALCULATION ---------------- #
if st.button("Run Dispatch"):

    # LOW LOAD
    if load <= (P1_min + P2_min):
        P1 = P1_min
        P2 = P2_min
        lambda_val = None
        status = "UNDER-LOADED"

    # HIGH LOAD
    elif load >= (P1_max + P2_max):
        P1 = P1_max
        P2 = P2_max
        lambda_val = None
        status = "OVERLOADED"

    # NORMAL CASE
    else:
        lambda_val = (load + (b1/a1) + (b2/a2)) / ((1/a1) + (1/a2))

        P1 = (lambda_val - b1) / (2*a1)
        P2 = (lambda_val - b2) / (2*a2)

        # Apply limits
        P1 = max(min(P1, P1_max), P1_min)
        P2 = max(min(P2, P2_max), P2_min)

        # Balance properly
        total = P1 + P2
        diff = load - total

        if abs(diff) > 0.01:
            if b1 < b2:
                P1 = min(P1 + diff, P1_max)
            elif b2 < b1:
                P2 = min(P2 + diff, P2_max)
            else:
                P1 += diff / 2
                P2 += diff / 2

        status = "NORMAL"

    total = P1 + P2

    # ---------------- COST ---------------- #
    cost1 = a1 * P1**2 + b1 * P1
    cost2 = a2 * P2**2 + b2 * P2
    total_cost = cost1 + cost2

    # ---------------- SYSTEM METRICS ---------------- #
    utilization = (total / (P1_max + P2_max)) * 100
    loss = 0.05 * total   # 5% assumed loss

    # ---------------- OUTPUT ---------------- #
    st.subheader("📊 Dispatch Results")

    c1, c2, c3 = st.columns(3)
    c1.metric("Generator 1", f"{P1:.2f} MW")
    c2.metric("Generator 2", f"{P2:.2f} MW")
    c3.metric("Total Generation", f"{total:.2f} MW")

    st.write(f"**Lambda (λ):** {lambda_val if lambda_val else 'N/A'}")
    st.write(f"**Total Cost:** ₹{total_cost:.2f}")

    # ---------------- SYSTEM STATUS ---------------- #
    st.subheader("🟢 System Status")

    if status == "UNDER-LOADED":
        st.error("🔴 UNDER-LOADED SYSTEM (Minimum constraint active)")
    elif status == "OVERLOADED":
        st.error("🔴 OVERLOADED SYSTEM (Maximum capacity reached)")
    else:
        st.success("🟢 NORMAL OPERATION")

    # ---------------- EXTRA METRICS ---------------- #
    st.subheader("⚙️ System Metrics")

    m1, m2 = st.columns(2)
    m1.metric("System Utilization", f"{utilization:.2f}%")
    m2.metric("Estimated Loss", f"{loss:.2f} MW")

    # ---------------- INSIGHT ---------------- #
    st.subheader("📌 Operator Recommendation")

    if b1 < b2:
        st.info("Increase Generator 1 output for better cost efficiency.")
    elif b2 < b1:
        st.info("Increase Generator 2 output for better cost efficiency.")
    else:
        st.info("Both generators share load equally for optimal operation.")

    # ---------------- BAR CHART ---------------- #
    st.subheader("📉 Generation Distribution")
    st.bar_chart({
        "G1": [P1],
        "G2": [P2]
    })

    # ---------------- COST CURVES ---------------- #
    st.subheader("📈 Cost Curves")

    P_range = np.linspace(0, 250, 100)
    cost_curve1 = a1 * P_range**2 + b1 * P_range
    cost_curve2 = a2 * P_range**2 + b2 * P_range

    df = pd.DataFrame({
        "Power": P_range,
        "Generator 1 Cost": cost_curve1,
        "Generator 2 Cost": cost_curve2
    })

    st.line_chart(df.set_index("Power"))
