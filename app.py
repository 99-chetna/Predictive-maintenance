import streamlit as st
import pandas as pd
from motion_detection import get_vibration_intensity

st.title("📹 Real-Time Vibration Monitoring System")
st.write("Using Camera Feed (No Randomness)")

ip = st.text_input("Enter DroidCam IP Address", "192.168.43.1")
duration = st.slider("Capture Duration (seconds)", 5, 60, 15)

if st.button("Start Monitoring"):
    st.info("⏳ Capturing real vibration data...")
    get_vibration_intensity(ip, duration)
    st.success("✅ Capture complete! Refresh to view new data.")

# Display logged data if available
try:
    df = pd.read_csv("vibration_log.csv")
    st.line_chart(df.set_index("timestamp"))
    st.write(df.tail())
except FileNotFoundError:
    st.warning("No vibration data found yet. Run capture first.")  