import streamlit as st
import pandas as pd
import os
from motion_detection import get_vibration_intensity

# ---------------------------------------------
# 🧭 App Configuration
# ---------------------------------------------
st.set_page_config(page_title="Vibration Monitor", layout="wide")
st.title("📹 Real-Time Vibration Monitoring System")
st.caption("Using Camera Feed — No Randomness, Continuous Logging to CSV")

# ---------------------------------------------
# ⚙️ User Inputs
# ---------------------------------------------
ip = st.text_input("Enter DroidCam IP Address", "192.168.43.1")
duration = st.slider("Capture Duration (seconds)", 5, 60, 15)
log_file = "vibration_log.csv"

# ---------------------------------------------
# 🧩 Placeholders for live updates
# ---------------------------------------------
chart_placeholder = st.empty()
status_placeholder = st.empty()
progress_bar = st.progress(0)

# ---------------------------------------------
# 🧠 Callback for live updates (from motion_detection)
# ---------------------------------------------
def update_live_chart(timestamp, value):
    # Append to Streamlit session dataframe
    new_data = pd.DataFrame([[timestamp, value]], columns=["timestamp", "intensity"])
    if "live_data" not in st.session_state:
        st.session_state.live_data = new_data
    else:
        st.session_state.live_data = pd.concat([st.session_state.live_data, new_data], ignore_index=True)

    # Show live updating chart
    chart_placeholder.line_chart(st.session_state.live_data.set_index("timestamp")["intensity"])

# ---------------------------------------------
# 🚀 Start Monitoring
# ---------------------------------------------
if st.button("Start Monitoring"):
    st.info("⏳ Capturing real vibration data...")
    st.session_state.live_data = pd.DataFrame(columns=["timestamp", "intensity"])
    get_vibration_intensity(ip, duration, log_file=log_file, progress_callback=update_live_chart)
    st.success("✅ Capture complete! Data stored automatically in vibration_log.csv")

# ---------------------------------------------
# 📋 Show Latest Stored Data (No historical graph)
# ---------------------------------------------
if os.path.exists(log_file) and os.stat(log_file).st_size > 0:
    try:
        df = pd.read_csv(log_file)
        if not df.empty:
            st.subheader("🗂️ Latest Vibration Readings (Auto-Logged)")
            st.dataframe(df.tail(20), use_container_width=True)
        else:
            st.warning("⚠️ The log file is empty. Start monitoring first.")
    except Exception as e:
        st.error(f"Error loading data: {e}")
else:
    st.warning("📁 No vibration data file found. Please start monitoring first.")
