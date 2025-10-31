import streamlit as st
import pandas as pd
import os
from motion_detection import get_vibration_intensity

# ---------------------------------------------
# 🧭 App Configuration
# ---------------------------------------------
st.set_page_config(page_title="Vibration Monitor", layout="wide")
st.title("📹 Real-Time Vibration Monitoring System")
st.caption("Using Camera Feed — No Randomness, Continuous Logging to CSV + Health Scoring")

# ---------------------------------------------
# ⚙️ User Inputs
# ---------------------------------------------
ip = st.text_input("Enter DroidCam IP Address", "192.168.43.1")
duration = st.slider("Capture Duration (seconds)", 5, 60, 15)
log_file = "vibration_log.csv"
threshold = st.number_input("⚙️ Set Vibration Threshold (for Maintenance Alerts)", min_value=10, max_value=100, value=40)

# ---------------------------------------------
# 🧩 Placeholders for live updates
# ---------------------------------------------
chart_placeholder = st.empty()
status_placeholder = st.empty()
progress_bar = st.progress(0)
health_placeholder = st.empty()

# ---------------------------------------------
# 🧠 Callback for live updates (from motion_detection)
# ---------------------------------------------
def update_live_chart(timestamp, value):
    new_data = pd.DataFrame([[timestamp, value]], columns=["timestamp", "intensity"])
    if "live_data" not in st.session_state:
        st.session_state.live_data = new_data
    else:
        st.session_state.live_data = pd.concat([st.session_state.live_data, new_data], ignore_index=True)
    
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
# 📊 Analyze and Display Stored Data
# ---------------------------------------------
if os.path.exists(log_file) and os.stat(log_file).st_size > 0:
    try:
        df = pd.read_csv(log_file)
        if not df.empty:
            st.subheader("🗂️ Latest Vibration Readings (Auto-Logged)")

            # Maintenance Status Column
            df["Status"] = df["intensity"].apply(lambda x: "⚠️ Fault" if x > threshold else "✅ Normal")

            # Calculate Machine Health Score (Inverse of average vibration)
            avg_intensity = df["intensity"].tail(30).mean()
            max_intensity = max(df["intensity"].max(), threshold + 10)
            health_score = max(0, min(100, 100 - (avg_intensity / max_intensity) * 100))

            # Show Score and Maintenance Alert
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🧠 Machine Health Score", f"{health_score:.1f} / 100")
            with col2:
                if health_score < 50 or df["intensity"].iloc[-1] > threshold:
                    st.error("🚨 Maintenance Needed — High Vibration Detected")
                else:
                    st.success("✅ Machine Operating Normally")

            # Color-coded styling for table
            def highlight_status(row):
                color = "#ffcccc" if row["Status"] == "⚠️ Fault" else "#ccffcc"
                return ["background-color: {}".format(color) if col == "Status" else "" for col in row.index]

            st.dataframe(df.tail(20).style.apply(highlight_status, axis=1), use_container_width=True)

        else:
            st.warning("⚠️ The log file is empty. Start monitoring first.")
    except Exception as e:
        st.error(f"Error loading data: {e}")
else:
    st.warning("📁 No vibration data file found. Please start monitoring first.")
