import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Smart Economic Dispatch", layout="wide")

st.title("⚡ Smart Economic Dispatch Simulator (PSOC)")

# ---------------- INPUTS ---------------- #
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
        status = "⚠️ Minimum generation constraint active"
        lambda_val = None

    # HIGH LOAD
    elif load >= (P1_max + P2_max):
        P1 = P1_max
        P2 = P2_max
        status = "⚠️ Maximum generation limit reached"
        lambda_val = None

    # NORMAL ECONOMIC DISPATCH
    else:
        lambda_val = (load + (b1/a1) + (b2/a2)) / ((1/a1) + (1/a2))

        P1 = (lambda_val - b1) / (2*a1)
        P2 = (lambda_val - b2) / (2*a2)

        # Apply limits
        P1 = max(min(P1, P1_max), P1_min)
        P2 = max(min(P2, P2_max), P2_min)

        # Balance
        total = P1 + P2
        diff = load - total

        if abs(diff) > 0.01:
          if b1 < b2:
             P1 = min(P1 + diff, P1_max)
          elif b2 < b1:
             P2 = min(P2 + diff, P2_max)
          else:
             # Equal cost → split evenly
              P1 += diff / 2
              P2 += diff / 2

        status = "✅ Economic dispatch successful"

    total = P1 + P2

    # ---------------- COST ---------------- #
    cost1 = a1 * P1**2 + b1 * P1
    cost2 = a2 * P2**2 + b2 * P2
    total_cost = cost1 + cost2

    # ---------------- OUTPUT ---------------- #
    st.subheader("📊 Dispatch Results")

    c1, c2, c3 = st.columns(3)
    c1.metric("Generator 1", f"{P1:.2f} MW")
    c2.metric("Generator 2", f"{P2:.2f} MW")
    c3.metric("Total Generation", f"{total:.2f} MW")

    st.write(f"**Lambda (λ):** {lambda_val if lambda_val else 'N/A'}")
    st.write(f"**Total Cost:** ₹{total_cost:.2f}")
    st.write(f"**Status:** {status}")

    # ---------------- INSIGHT ---------------- #
    st.subheader("🧠 Insights")

    if b1 < b2:
        st.success("Generator 1 is more economical → carries more load")
    elif b2 < b1:
        st.success("Generator 2 is more economical → carries more load")
    else:
        st.info("Both generators have similar cost → equal sharing")

    # ---------------- CHART ---------------- #
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