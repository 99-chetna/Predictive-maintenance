import streamlit as st
import pandas as pd
import os
from motion_detection import get_vibration_intensity

# ==============================
# 🔧 PAGE SETUP
# ==============================
st.set_page_config(
    page_title="Real-Time Predictive Maintenance Dashboard",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Real-Time Predictive Maintenance System")
st.markdown("### Powered by OpenCV + Streamlit (Camera-Based Vibration Detection)")
st.markdown("---")

# ==============================
# 🧠 USER INPUTS
# ==============================
st.sidebar.header("📷 Camera Configuration")
ip = st.sidebar.text_input("Enter DroidCam IP Address", "192.168.43.1")
duration = st.sidebar.slider("Capture Duration (seconds)", 5, 60, 15)
threshold = st.sidebar.number_input("Set Vibration Threshold", min_value=10, max_value=200, value=50)

# ==============================
# 🎥 START DATA CAPTURE
# ==============================
if st.button("🚀 Start Monitoring"):
    st.info("📡 Connecting to camera and capturing real-time vibration data...")
    get_vibration_intensity(ip, duration)
    st.success("✅ Capture complete! Data saved to `vibration_log.csv`.")

# ==============================
# 📊 LOAD & DISPLAY DATA
# ==============================
if os.path.exists("vibration_log.csv"):
    df = pd.read_csv("vibration_log.csv")

    # Clean and preprocess
    df.dropna(inplace=True)
    if not df.empty:
        # Convert timestamps
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values(by="timestamp")

        # Add maintenance status
        df["status"] = df["intensity"].apply(
            lambda x: "⚠️ Fault" if x > threshold else "✅ Normal"
        )

        # Split layout
        col1, col2 = st.columns([2, 1])

        # 📈 Live Vibration Chart
        with col1:
            st.subheader("📈 Vibration Intensity Over Time")
            st.line_chart(df.set_index("timestamp")["intensity"])

        # 🔍 Latest Status
        with col2:
            st.subheader("🧠 Maintenance Status")
            latest_intensity = df["intensity"].iloc[-1]
            latest_status = "⚠️ Fault" if latest_intensity > threshold else "✅ Normal"

            st.metric("Latest Vibration Intensity", f"{latest_intensity:.2f}")
            if latest_status == "⚠️ Fault":
                st.error("🚨 High vibration detected! Maintenance Required.")
            else:
                st.success("✅ Machine Operating Normally.")

        # 🧾 Data Table
        st.markdown("---")
        st.subheader("🗂️ Recent Vibration Data")
        st.dataframe(df.tail(20), use_container_width=True)

        # 📊 Summary Stats
        st.markdown("---")
        st.subheader("📊 Statistical Summary")
        st.write(df.describe())

    else:
        st.warning("No data captured yet. Click 'Start Monitoring' above.")
else:
    st.warning("No vibration data file found. Please run a capture first.")
