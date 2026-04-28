import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
import time
import base64
from streamlit_autorefresh import st_autorefresh

# ---------- CONFIG & CLEAN UI ----------
st.set_page_config(layout="centered", page_title="PEMS Pro Dashboard")

# STYLING: Hiding branding and creating custom professional cards
style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {background-color: #0E1117;}
    
    /* Custom Card Design */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    .metric-label { color: #808495; font-size: 14px; margin-bottom: 5px; }
    .metric-value { color: #FFFFFF; font-size: 28px; font-weight: bold; }
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# Audio Alert Function (Hidden HTML)
def play_alarm():
    # A short, professional high-pitched beep
    sound_html = """
        <audio autoplay>
            <source src="https://www.soundjay.com/buttons/beep-01a.mp3" type="audio/mpeg">
        </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# --- TELEGRAM SETTINGS ---
BOT_TOKEN = "7872128863:AAEmJI6zvwn0sXkKuNjPEPsO_zHI3enG6rQ"
CHAT_ID = "PASTE_YOUR_CHAT_ID_HERE" # Put your ID from userinfobot here

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try: requests.get(url, timeout=5)
    except: pass

# ---------- APP TITLE ----------
st.markdown("<h1 style='text-align:center; color:white; font-size: 24px; margin-bottom:0;'>PEMS <span style='color:#FF4B4B;'>PRO</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555; margin-top:0;'>Environmental Intelligence System</p>", unsafe_allow_html=True)

READ_API = "BQKHJAWUIGJCQKXO"
CHANNEL_ID = "3358151"
DATA_FILE = "exposure_history.csv"

st_autorefresh(interval=2000, key="refresh")

# ---------- DATA PROCESSING ----------
if "data_cache" not in st.session_state:
    st.session_state.data_cache = {"AQI": "0", "TEMP": "0", "DB": "0", "UV": "0", "SCORE": "0"}
if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = 0

def fetch_data():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds/last.json?api_key={READ_API}"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        st.session_state.data_cache = {
            "AQI": data.get("field1", "0"),
            "TEMP": data.get("field2", "0"),
            "DB": data.get("field3", "0"),
            "UV": data.get("field4", "0"),
            "SCORE": data.get("field5", "0")
        }
    except: pass

fetch_data()
c = st.session_state.data_cache
def sf(v):
    try: return float(v)
    except: return 0

score, aqi, temp, noise, uv = sf(c["SCORE"]), sf(c["AQI"]), sf(c["TEMP"]), sf(c["DB"]), sf(c["UV"])

# ---------- LOGIC & ALERTS ----------
if (score >= 90 or aqi >= 200):
    play_alarm() # Plays sound in the browser
    current_time = time.time()
    if current_time - st.session_state.last_alert_time > 300:
        send_telegram_msg(f"🚨 CRITICAL EXPOSURE: {int(score)}%")
        st.session_state.last_alert_time = current_time

# ---------- MODERN DASHBOARD UI ----------

# Metrics Grid
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>🍃 Air Quality</div><div class='metric-value'>{int(aqi)}</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>🌡️ Temperature</div><div class='metric-value'>{temp}°C</div></div>", unsafe_allow_html=True)

st.markdown("<div style='margin: 10px;'></div>", unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>🔊 Noise Level</div><div class='metric-value'>{int(noise)} dB</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>☀️ UV Index</div><div class='metric-value'>{uv}</div></div>", unsafe_allow_html=True)

# Main Exposure Display
st.markdown("---")
if score >= 90:
    color = "#FF4B4B"
    status = "CRITICAL DANGER"
elif score >= 70:
    color = "#FFA500"
    status = "MODERATE RISK"
else:
    color = "#00FF7F"
    status = "SAFE ENVIRONMENT"

st.markdown(f"""
    <div style='background: rgba(255,255,255,0.03); padding: 30px; border-radius: 20px; border: 1px solid {color}44; text-align: center;'>
        <p style='color: #888; letter-spacing: 2px; font-size: 12px; margin-bottom: 0;'>SYSTEM EXPOSURE SCORE</p>
        <h1 style='color: {color}; font-size: 100px; margin: 0; padding: 0;'>{int(score)}</h1>
        <div style='background: {color}22; color: {color}; padding: 5px 15px; border-radius: 50px; display: inline-block; font-weight: bold; font-size: 14px;'>
            {status}
        </div>
    </div>
""", unsafe_allow_html=True)

# Chart
st.markdown("<br>", unsafe_allow_html=True)
try:
    now = datetime.now().strftime("%H:%M:%S")
    df_new = pd.DataFrame([[now, score]], columns=["Time", "Score"])
    if os.path.exists(DATA_FILE): df_new.to_csv(DATA_FILE, mode="a", header=False, index=False)
    else: df_new.to_csv(DATA_FILE, index=False)
    df = pd.read_csv(DATA_FILE).tail(20)
    st.line_chart(df.set_index("Time"), color=color)
except: pass

st.caption("Secure Data Stream • PEMS Cloud v2.0")
