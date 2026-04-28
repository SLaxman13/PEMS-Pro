import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
import time
from streamlit_autorefresh import st_autorefresh

# ---------- CONFIG ----------
st.set_page_config(
    layout="centered",
    page_title="PEMS Pro"
)

# --- TELEGRAM SETTINGS ---
# Replace these with your actual details from Step 1
BOT_TOKEN = "7872128863:AAEmJI6zvwn0sXkKuNjPEPsO_zHI3enG6rQ"
CHAT_ID = "1368198170"

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        requests.get(url, timeout=5)
    except:
        pass

st.markdown(
    "<h2 style='text-align:center;'>🌍 Personalized Environmental Monitoring System</h2>",
    unsafe_allow_html=True
)

READ_API = "BQKHJAWUIGJCQKXO"
CHANNEL_ID = "3358151"
DATA_FILE = "exposure_history.csv"

# ---------- AUTO REFRESH ----------
st_autorefresh(interval=2000, key="refresh")

# ---------- SESSION STATE ----------
if "data_cache" not in st.session_state:
    st.session_state.data_cache = {"AQI": "0", "TEMP": "0", "DB": "0", "UV": "0", "SCORE": "0"}

if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = 0

# ---------- FETCH DATA ----------
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
    except:
        pass

fetch_data()
cache = st.session_state.data_cache

# ---------- SAFE CONVERSION ----------
def safe_float(val):
    try: return float(val)
    except: return 0

score = safe_float(cache["SCORE"])
aqi = safe_float(cache["AQI"])
temp = safe_float(cache["TEMP"])
noise = safe_float(cache["DB"])
uv = safe_float(cache["UV"])

# ---------- TELEGRAM ALERT LOGIC ----------
current_time = time.time()
# Check thresholds: Score >= 90 or AQI >= 200
if (score >= 90 or aqi >= 200):
    # This ensures it only sends one message every 5 minutes (300 seconds)
    if current_time - st.session_state.last_alert_time > 300:
        alert_msg = f"🚨 PEMS ALERT!\n⚠️ Exposure Score: {int(score)}%\n🍃 AQI: {int(aqi)}\n📍 Check your environment immediately."
        send_telegram_msg(alert_msg)
        st.session_state.last_alert_time = current_time

# ---------- UI ALERTS ----------
if score >= 90:
    st.error("🚨 HIGH RISK: Move to safer area immediately!")
elif score >= 70:
    st.warning("⚠️ MODERATE RISK: Be cautious")
elif score <= 20:
    st.success("✅ SAFE ENVIRONMENT")

# ---------- SAVE GRAPH DATA ----------
try:
    now = datetime.now().strftime("%H:%M:%S")
    df_new = pd.DataFrame([[now, score]], columns=["Time", "Score"])
    if os.path.exists(DATA_FILE):
        df_new.to_csv(DATA_FILE, mode="a", header=False, index=False)
    else:
        df_new.to_csv(DATA_FILE, index=False)
except:
    pass

# ---------- UI DASHBOARD ----------
st.markdown("### 📊 Live Sensor Dashboard")
col1, col2 = st.columns(2)
col1.metric("🍃 AQI", aqi)
col2.metric("🌡️ Temperature (°C)", temp)

col1, col2 = st.columns(2)
col1.metric("🔊 Noise (dB)", noise)
col2.metric("☀️ UV Index", uv)

st.markdown("---")
st.markdown("### ⚡ Exposure Score")

if score >= 90:
    st.markdown(f"<h1 style='color:red; text-align:center;'>{int(score)}</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:red; text-align:center;'>DANGER</h4>", unsafe_allow_html=True)
elif score >= 70:
    st.markdown(f"<h1 style='color:orange; text-align:center;'>{int(score)}</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:orange; text-align:center;'>MODERATE</h4>", unsafe_allow_html=True)
elif score <= 20:
    st.markdown(f"<h1 style='color:green; text-align:center;'>{int(score)}</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:green; text-align:center;'>SAFE</h4>", unsafe_allow_html=True)
else:
    st.markdown(f"<h1 style='text-align:center;'>{int(score)}</h1>", unsafe_allow_html=True)

# ---------- GRAPH ----------
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE)
        st.line_chart(df.set_index("Time").tail(30))
    except:
        pass

st.markdown("---")
st.caption("🔄 Auto-refresh every 2 seconds | PEMS Pro v1.0")
