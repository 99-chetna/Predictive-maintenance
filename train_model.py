import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os
from motion_detection import get_vibration_intensity

# ========================================
# PAGE SETUP
# ========================================
st.set_page_config(
    page_title="Machine Health Prediction Dashboard",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Predictive Maintenance & Machine Health Index")
st.caption("Camera-Based Real-Time Machine Health Monitoring using OpenCV & Streamlit")
st.markdown("---")

# ========================================
# USER INPUTS
# ========================================
st.sidebar.header("📷 Camera & Monitoring Settings")
ip = st.sidebar.text_input("Enter DroidCam IP Address", "192.168.43.1")
duration = st.sidebar.slider("Capture Duration (seconds)", 5, 60, 15)
threshold = st.sidebar.number_input("Set Vibration Warning Threshold", min_value=10, max_value=200, value=40)

# ========================================
# CAPTURE NEW DATA
# ========================================
if st.button("🚀 Start Vibration Capture"):
    st.info("🎥 Connecting to camera and capturing vibration data...")
    get_vibration_intensity(ip, duration)
    st.success("✅ Data successfully captured and saved to 'vibration_log.csv'")

# ========================================
# LOAD EXISTING DATA
# ========================================
if os.path.exists("vibration_log.csv"):
    df = pd.read_csv("vibration_log.csv")

    if not df.empty:
        df.dropna(inplace=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values(by="timestamp")

        # ========================================
        # CALCULATE METRICS
        # ========================================
        avg_intensity = np.mean(df["intensity"])
        peak_intensity = np.max(df["intensity"])
        current_intensity = df["intensity"].iloc[-1]

        # -------------------------------
        # 🧠 MACHINE HEALTH SCORE
        # -------------------------------
        # Formula: Higher vibration = Lower health
        health_score = max(0, 100 - (avg_intensity * 2))

        if health_score > 75:
            status = "✅ Excellent - Machine Healthy"
        elif 45 <= health_score <= 75:
            status = "⚠️ Moderate - Monitor Regularly"
        else:
            status = "🔴 Poor - Maintenance Required"

        # ========================================
        # DISPLAY DASHBOARD METRICS
        # ========================================
        st.markdown("## 📊 Machine Status Overview")
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("📉 Avg Vibration", f"{avg_intensity:.2f}")
        col2.metric("⚡ Peak Vibration", f"{peak_intensity:.2f}")
        col3.metric("🎯 Current Intensity", f"{current_intensity:.2f}")
        col4.metric("💚 Health Score", f"{health_score:.1f} %")

        st.markdown(f"### Current Status: {status}")
        if health_score < 45:
            st.error("🚨 Machine Health Low – Immediate Maintenance Advised.")
        elif 45 <= health_score <= 75:
            st.warning("⚠️ Moderate Condition – Monitor Vibration Trends.")
        else:
            st.success("✅ Machine Operating Normally and Stable.")

        st.markdown("---")

        # ========================================
        # 📈 VIBRATION TREND CHART
        # ========================================
        st.subheader("📈 Vibration Intensity Over Time (Last 50 Readings)")
        chart = (
            alt.Chart(df.tail(50))
            .mark_line(point=True)
            .encode(
                x=alt.X("timestamp:T", title="Time"),
                y=alt.Y("intensity:Q", title="Vibration Intensity"),
                tooltip=["timestamp", "intensity"]
            )
            .properties(width=850, height=350, title="Real-Time Vibration Trend")
        )
        st.altair_chart(chart, use_container_width=True)

        # ========================================
        # 📊 HISTORICAL HEALTH TREND
        # ========================================
        df["health_score"] = 100 - (df["intensity"] * 2)
        df["health_score"] = df["health_score"].clip(lower=0)

        st.subheader("📉 Machine Health Trend Over Time")
        health_chart = (
            alt.Chart(df.tail(50))
            .mark_area(opacity=0.5)
            .encode(
                x="timestamp:T",
                y="health_score:Q",
                tooltip=["timestamp", "health_score"]
            )
            .properties(width=850, height=250, title="Health Score Variation")
        )
        st.altair_chart(health_chart, use_container_width=True)

        # ========================================
        # 🧾 RECENT DATA TABLE
        # ========================================
        st.markdown("---")
        st.subheader("🗂 Recent Logged Data")
        st.dataframe(df.tail(20), use_container_width=True)

        # ========================================
        # 📊 SUMMARY STATISTICS
        # ========================================
        st.markdown("---")
        st.subheader("📊 Statistical Summary")
        st.write(df.describe())

    else:
        st.warning("⚠️ No data captured yet. Please capture vibration data first.")
else:
    st.warning("📂 No 'vibration_log.csv' found. Run a capture to start logging data.")
