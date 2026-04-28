import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os
import time
from streamlit_autorefresh import st_autorefresh

# ---------- CONFIG & ULTRA-CLEAN UI ----------
# We use centered layout to force a professional column width on mobile.
st.set_page_config(layout="centered", page_title="PEMS PRO")

# Full CSS Override for professional look and dark theme unity
style = """
    <style>
    /* Hide all standard Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 2rem; padding-bottom: 0rem;}
    
    /* Set main app background to a sophisticated deep charcoal */
    .stApp {background-color: #121419;}
    
    /* Clean, professional font overrides (no AI vibe) */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #E0E0E0;
    }

    /* Target the container that holds columns to force exact centering and alignment */
    [data-testid="stHorizontalBlock"] {
        align-items: center !important;
        justify-content: center !important;
    }

    /* Fix column alignment to prevent the messy stacking */
    [data-testid="column"] {
        flex: 1 1 45% !important;  /* Force columns to take up ~half width, preventing list view */
        max-width: 45% !important;
        min-width: 45% !important;
        margin: 5px !important;
    }

    /* Make the metrics look professional and aligned */
    [data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        text-align: center !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px !important;
        color: #909090 !important;
        text-align: center !important;
    }

    /* Re-align titles to be truly centered */
    h1, h2, h3, h4, p {text-align: center !important;}

    /* DARK GRAPH UNITY (The key fix) */
    #deckgl-wrapper {background-color: #121419 !important;}
    .vega-bind {color: #E0E0E0 !important;}
    
    /* The line color of the graph */
    [data-testid="stLineChart"] path.path-bg {
        stroke: #FF4B4B !important; 
        stroke-opacity: 1 !important;
    }
    
    /* Grid lines of the graph (no white) */
    [data-testid="stLineChart"] .vega-actions-light {
        color: #666 !important;
    }

    </style>
"""
st.markdown(style, unsafe_allow_html=True)

# --- TELEGRAM SETTINGS (Paste your credentials) ---
BOT_TOKEN = "7872128863:AAEmJI6zvwn0sXkKuNjPEPsO_zHI3enG6rQ"
CHAT_ID = "PASTE_YOUR_CHAT_ID_HERE" # Put your ID from userinfobot here

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try: requests.get(url, timeout=5)
    except: pass

# ---------- PRECISE TITLE ALIGNMENT ----------
st.markdown("<h1 style='color:white; font-size: 36px; margin-bottom: 0px;'>PEMS</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='color:#FF4B4B; font-size: 16px; margin-top: -5px; margin-bottom: 25px; letter-spacing: 1px;'>Environmental Monitoring System</h3>", unsafe_allow_html=True)

READ_API = "BQKHJAWUIGJCQKXO"
CHANNEL_ID = "3358151"
DATA_FILE = "exposure_history.csv"

# ---------- AUTO REFRESH ----------
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

# ---------- ALERT LOGIC ----------
if (score >= 90 or aqi >= 200):
    current_time = time.time()
    if current_time - st.session_state.last_alert_time > 300:
        send_telegram_msg(f"🚨 CRITICAL EXPOSURE DETECTED: {int(score)}%")
        st.session_state.last_alert_time = current_time

# ---------- HAND-CODED ALIGNED UI DASHBOARD ----------
# st.write("---") # Optional separating line

# Row 1: Forced side-by-side on mobile
# We use st.columns(2) inside a custom block to force alignment.
c1, c2 = st.columns(2)
# We add spacing HTML before the metrics to ensure they are vertically centered in their imaginary grid
c1.markdown("<br>", unsafe_allow_html=True)
c1.metric(label="🍃 Air Quality", value=f"{int(aqi)}")
c2.markdown("<br>", unsafe_allow_html=True)
c2.metric(label="🌡️ Temperature", value=f"{temp:.1f}°C")

# Clean vertical gap
st.markdown("<div style='margin: 15px;'></div>", unsafe_allow_html=True)

# Row 2: Forced side-by-side
c3, c4 = st.columns(2)
c3.markdown("<br>", unsafe_allow_html=True)
c3.metric(label="🔊 Noise Level", value=f"{int(noise)} dB")
c4.markdown("<br>", unsafe_allow_html=True)
c4.metric(label="☀️ UV Index", value=f"{uv:.1f}")

# Main Exposure Display
st.markdown("---")
st.markdown("<h4 style='color: #888; font-size: 14px; margin-bottom:-10px;'>Personalized Exposure</h4>", unsafe_allow_html=True)

if score >= 90:
    color = "#FF4B4B" # Red
    status = "CRITICAL DANGER"
elif score >= 70:
    color = "#FFA500" # Orange
    status = "MODERATE RISK"
else:
    color = "#00FF7F" # Green
    status = "SAFE ENVIRONMENT"

st.markdown(f"<h1 style='color: {color}; font-size: 100px; margin: 0; padding: 0;'>{int(score)}</h1>", unsafe_allow_html=True)

# The centered, colored status pill
st.markdown(f"""
    <div style='text-align:center;'>
        <div style='background: {color}11; color: {color}; padding: 5px 20px; border-radius: 50px; display: inline-block; font-weight: bold; font-size: 14px; border: 1px solid {color}44; text-align: center;'>
            {status}
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------- DARK GRAPH SECTION (UNITY FIX) ----------
st.markdown("<br>", unsafe_allow_html=True)
#st.markdown("### 📈 Exposure Trend (Last 30 Min)")

try:
    now = datetime.now().strftime("%H:%M:%S")
    df_new = pd.DataFrame([[now, score]], columns=["Time", "Score"])
    if os.path.exists(DATA_FILE): df_new.to_csv(DATA_FILE, mode="a", header=False, index=False)
    else: df_new.to_csv(DATA_FILE, index=False)
    df = pd.read_csv(DATA_FILE).tail(30)
    
    # st.line_chart is notoriously hard to fully theme. 
    # For unity, we force its line color to match the threat level and rely on our full-app dark background to make it look cohesive.
    st.line_chart(df.set_index("Time"), color=color)
    
except: pass

st.markdown("---")
st.caption("PEMS Cloud v2.1 | Data Secure Stream")
