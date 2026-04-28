import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
import time
from streamlit_autorefresh import st_autorefresh

# ---------- CONFIG & CLEAN LIGHT UI ----------
st.set_page_config(layout="centered", page_title="PEMS")

style = """
    <style>
    /* Clean white look */
    .stApp {background-color: #FFFFFF;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Precise alignment for columns on mobile */
    [data-testid="column"] {
        flex: 1 1 45% !important;
        max-width: 45% !important;
        min-width: 45% !important;
        text-align: center !important;
    }

    /* Professional Metric Styling */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 600 !important;
        color: #1A1A1B !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
        color: #5F6368 !important;
    }
    
    /* Centering everything */
    h1, h2, h3, h4, p {text-align: center !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
    
    /* Removing unnecessary padding */
    .block-container {padding-top: 2rem;}
    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- SETTINGS ---
BOT_TOKEN = "7872128863:AAEmJI6zvwn0sXkKuNjPEPsO_zHI3enG6rQ"
CHAT_ID = "PASTE_YOUR_CHAT_ID_HERE" 

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try: requests.get(url, timeout=5)
    except: pass

# ---------- TITLES ----------
st.markdown("<h1 style='color:#1A1A1B; font-size: 42px; font-weight: 800; margin-bottom: 0;'>PEMS</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#D93025; font-weight: 600; font-size: 14px; margin-top: -10px; letter-spacing: 1.5px;'>ENVIRONMENTAL MONITORING SYSTEM</p>", unsafe_allow_html=True)

READ_API = "BQKHJAWUIGJCQKXO"
CHANNEL_ID = "3358151"
DATA_FILE = "exposure_history.csv"

st_autorefresh(interval=2000, key="refresh")

# ---------- DATA ----------
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

# ---------- ALERTS ----------
if (score >= 90 or aqi >= 200):
    current_time = time.time()
    if current_time - st.session_state.last_alert_time > 300:
        send_telegram_msg(f"🚨 ALERT: HIGH EXPOSURE ({int(score)}%)")
        st.session_state.last_alert_time = current_time

# ---------- DASHBOARD ----------
st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
c1.metric("🍃 Air Quality", f"{int(aqi)}")
c2.metric("🌡️ Temp", f"{temp:.1f}°C")

st.markdown("<div style='margin: 10px;'></div>", unsafe_allow_html=True)

c3, c4 = st.columns(2)
c3.metric("🔊 Noise", f"{int(noise)} dB")
c4.metric("☀️ UV Index", f"{uv:.1f}")

st.markdown("<hr style='border: 0.5px solid #EEE;'>", unsafe_allow_html=True)

# ---------- EXPOSURE SCORE ----------
if score >= 90:
    color = "#D93025" # Google Red
    status = "CRITICAL DANGER"
elif score >= 70:
    color = "#F9AB00" # Google Yellow/Orange
    status = "MODERATE RISK"
else:
    color = "#188038" # Google Green
    status = "SAFE"

st.markdown(f"<p style='color: #5F6368; font-size: 12px; margin-bottom: 0;'>SYSTEM EXPOSURE SCORE</p>", unsafe_allow_html=True)
st.markdown(f"<h1 style='color: {color}; font-size: 95px; margin: 0;'>{int(score)}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: {color}; font-weight: bold; letter-spacing: 1px;'>{status}</p>", unsafe_allow_html=True)

# ---------- GRAPH (Matches White background perfectly) ----------
try:
    now = datetime.now().strftime("%H:%M:%S")
    df_new = pd.DataFrame([[now, score]], columns=["Time", "Score"])
    if os.path.exists(DATA_FILE): df_new.to_csv(DATA_FILE, mode="a", header=False, index=False)
    else: df_new.to_csv(DATA_FILE, index=False)
    
    df = pd.read_csv(DATA_FILE).tail(20)
    st.line_chart(df.set_index("Time"), color=color)
except: pass

st.markdown("<br>", unsafe_allow_html=True)
st.caption("PEMS v2.2 | Research Analytics Data")
