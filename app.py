# ============================================================
#  CryptoScan Pro – Premium Trading Scanner
#  Streamlit App  |  Dark Terminal FinTech UI
#  Signale: RSI < 30  +  EMA200-Kreuzung
# ============================================================
#
#  Installation:
#    pip install streamlit yfinance pandas plotly requests
#
#  Starten:
#    streamlit run app.py

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import time
from datetime import datetime, timedelta

# ── Seitenkonfiguration (MUSS als erstes stehen) ─────────────
st.set_page_config(
    page_title="CryptoScan Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════
#  PREMIUM CSS – Dark Terminal FinTech
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;600&display=swap');

/* ── Reset & Base ───────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background: #080B10 !important;
    color: #C8D6E5 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 40% at 20% -10%, rgba(0,245,212,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 60% 30% at 80% 110%, rgba(0,100,255,0.05) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
footer { display: none !important; }

/* ── Sidebar ────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0C0F16 !important;
    border-right: 1px solid rgba(0,245,212,0.08) !important;
}

/* ── Header ─────────────────────────────────────────────── */
.cs-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 28px 0 24px 0;
    border-bottom: 1px solid rgba(0,245,212,0.12);
    margin-bottom: 32px;
}
.cs-logo {
    display: flex;
    align-items: center;
    gap: 14px;
}
.cs-logo-icon {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #00F5D4, #0066FF);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    box-shadow: 0 0 20px rgba(0,245,212,0.3);
}
.cs-logo-text {
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: #EDF2F7;
}
.cs-logo-text span {
    color: #00F5D4;
}
.cs-timestamp {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #4A5568;
    text-align: right;
    line-height: 1.8;
}
.cs-timestamp b {
    color: #00F5D4;
    font-weight: 600;
}

/* ── Metric Cards ───────────────────────────────────────── */
.cs-cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
.cs-card {
    background: linear-gradient(135deg, #0D1117 0%, #111827 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
}
.cs-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--card-accent, #00F5D4);
    opacity: 0.7;
}
.cs-card:hover {
    border-color: rgba(0,245,212,0.2);
    transform: translateY(-2px);
}
.cs-card-icon {
    font-size: 22px;
    margin-bottom: 10px;
    display: block;
}
.cs-card-label {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #4A5568;
    margin-bottom: 6px;
}
.cs-card-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 600;
    color: #EDF2F7;
    line-height: 1;
}
.cs-card-sub {
    font-size: 12px;
    color: #4A5568;
    margin-top: 6px;
}

/* ── Scan Button ────────────────────────────────────────── */
.stButton > button {
    width: 100%;
    padding: 16px 32px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    color: #080B10 !important;
    background: linear-gradient(90deg, #00F5D4 0%, #0066FF 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    box-shadow: 0 4px 24px rgba(0,245,212,0.25) !important;
}
.stButton > button:hover {
    transform: scale(1.02) !important;
    box-shadow: 0 6px 32px rgba(0,245,212,0.4) !important;
}
.stButton > button:active {
    transform: scale(0.99) !important;
}

/* ── Progress Bar ───────────────────────────────────────── */
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #00F5D4, #0066FF) !important;
    border-radius: 99px !important;
}
[data-testid="stProgressBar"] > div {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 99px !important;
    height: 6px !important;
}

/* ── Tabs ───────────────────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
    gap: 4px !important;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #4A5568 !important;
    padding: 10px 20px !important;
    border-radius: 8px 8px 0 0 !important;
    border: none !important;
    background: transparent !important;
    transition: color 0.2s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #00F5D4 !important;
    background: rgba(0,245,212,0.06) !important;
    border-bottom: 2px solid #00F5D4 !important;
}
[data-testid="stTabs"] [role="tab"]:hover {
    color: #C8D6E5 !important;
}

/* ── Dataframe / Table ──────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] table {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
}

/* ── Signal Table (custom HTML) ─────────────────────────── */
.cs-table-wrap {
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    overflow: hidden;
    margin-top: 8px;
}
.cs-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}
.cs-table thead tr {
    background: #0D1117;
    border-bottom: 1px solid rgba(0,245,212,0.15);
}
.cs-table thead th {
    padding: 13px 16px;
    text-align: left;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.3px;
    text-transform: uppercase;
    color: #4A5568;
    white-space: nowrap;
}
.cs-table tbody tr {
    border-bottom: 1px solid rgba(255,255,255,0.03);
    transition: background 0.15s;
}
.cs-table tbody tr:hover {
    background: rgba(0,245,212,0.04);
}
.cs-table tbody td {
    padding: 12px 16px;
    font-family: 'JetBrains Mono', monospace;
    color: #C8D6E5;
    white-space: nowrap;
}
.cs-table tbody td.ticker {
    font-weight: 600;
    color: #EDF2F7;
    letter-spacing: 0.5px;
}
.cs-table tbody td.ticker a {
    color: #00F5D4;
    text-decoration: none;
}
.cs-table tbody td.ticker a:hover {
    text-decoration: underline;
}

/* ── Badges ─────────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.badge-red    { background: rgba(255,61,0,0.12);  color: #FF6B6B; border: 1px solid rgba(255,61,0,0.25); }
.badge-green  { background: rgba(0,230,118,0.10); color: #00E676; border: 1px solid rgba(0,230,118,0.25); }
.badge-teal   { background: rgba(0,245,212,0.10); color: #00F5D4; border: 1px solid rgba(0,245,212,0.25); }
.badge-yellow { background: rgba(255,214,0,0.10); color: #FFD600; border: 1px solid rgba(255,214,0,0.25); }
.badge-gray   { background: rgba(255,255,255,0.05); color: #4A5568; border: 1px solid rgba(255,255,255,0.08); }

/* ── Tooltip ─────────────────────────────────────────────── */
.cs-tooltip {
    position: relative;
    display: inline-block;
    cursor: help;
    color: #4A5568;
    font-size: 12px;
    margin-left: 5px;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 50%;
    width: 16px; height: 16px;
    line-height: 14px;
    text-align: center;
    font-family: 'Space Grotesk', sans-serif;
}
.cs-tooltip:hover .cs-tooltip-text {
    visibility: visible;
    opacity: 1;
}
.cs-tooltip-text {
    visibility: hidden;
    opacity: 0;
    width: 240px;
    background: #1A2035;
    color: #C8D6E5;
    font-size: 12px;
    font-family: 'Space Grotesk', sans-serif;
    line-height: 1.6;
    border-radius: 8px;
    padding: 12px 14px;
    border: 1px solid rgba(0,245,212,0.15);
    position: absolute;
    z-index: 999;
    bottom: 130%;
    left: 50%;
    transform: translateX(-50%);
    transition: opacity 0.2s;
    pointer-events: none;
}

/* ── Section title ───────────────────────────────────────── */
.cs-section-title {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #4A5568;
    margin: 28px 0 14px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.cs-section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.05);
}

/* ── Empty state ─────────────────────────────────────────── */
.cs-empty {
    text-align: center;
    padding: 60px 20px;
    color: #2D3748;
}
.cs-empty-icon { font-size: 48px; margin-bottom: 16px; }
.cs-empty-text { font-size: 15px; }

/* ── Selectbox / Input ───────────────────────────────────── */
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background: #0D1117 !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    color: #C8D6E5 !important;
}

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #080B10; }
::-webkit-scrollbar-thumb { background: #1A2035; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #2D3748; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  KONFIGURATION
# ════════════════════════════════════════════════════════════
TOP50_AKTIEN = [
    "AAPL","MSFT","NVDA","AMZN","GOOGL","META","TSLA","BRK-B",
    "JPM","LLY","V","UNH","XOM","MA","JNJ","PG",
    "HD","COST","AVGO","MRK","CVX","ABBV","KO","PEP",
    "BAC","ADBE","WMT","MCD","CRM","ACN","TMO","CSCO",
    "ABT","LIN","TXN","DHR","NEE","NKE","PM","ORCL",
    "INTC","AMD","QCOM","MS","RTX","HON","IBM","GE","CAT","AMGN"
]
TOP50_KRYPTO = [
    "BTC-USD","ETH-USD","BNB-USD","SOL-USD","XRP-USD",
    "ADA-USD","AVAX-USD","DOGE-USD","DOT-USD","TRX-USD",
    "LINK-USD","MATIC-USD","LTC-USD","SHIB-USD","BCH-USD",
    "UNI-USD","ATOM-USD","XLM-USD","ETC-USD","ICP-USD",
    "FIL-USD","HBAR-USD","VET-USD","APT-USD","NEAR-USD",
    "ARB-USD","OP-USD","MKR-USD","GRT-USD","AAVE-USD",
    "STX-USD","INJ-USD","RUNE-USD","IMX-USD","FTM-USD",
    "SAND-USD","MANA-USD","AXS-USD","THETA-USD","EOS-USD",
    "EGLD-USD","XMR-USD","ALGO-USD","FLOW-USD","KCS-USD",
    "CHZ-USD","ZEC-USD","DASH-USD","BAT-USD","ENJ-USD"
]
TV_EXCHANGE = {
    "BTC-USD":"BINANCE:BTCUSDT","ETH-USD":"BINANCE:ETHUSDT",
    "BNB-USD":"BINANCE:BNBUSDT","SOL-USD":"BINANCE:SOLUSDT",
    "XRP-USD":"BINANCE:XRPUSDT","ADA-USD":"BINANCE:ADAUSDT",
    "AVAX-USD":"BINANCE:AVAXUSDT","DOGE-USD":"BINANCE:DOGEUSDT",
    "DOT-USD":"BINANCE:DOTUSDT","TRX-USD":"BINANCE:TRXUSDT",
    "LINK-USD":"BINANCE:LINKUSDT","MATIC-USD":"BINANCE:MATICUSDT",
    "LTC-USD":"BINANCE:LTCUSDT","SHIB-USD":"BINANCE:SHIBUSDT",
    "BCH-USD":"BINANCE:BCHUSDT","UNI-USD":"BINANCE:UNIUSDT",
    "ATOM-USD":"BINANCE:ATOMUSDT","XLM-USD":"BINANCE:XLMUSDT",
    "ETC-USD":"BINANCE:ETCUSDT","ICP-USD":"BINANCE:ICPUSDT",
    "FIL-USD":"BINANCE:FILUSDT","HBAR-USD":"BINANCE:HBARUSDT",
    "VET-USD":"BINANCE:VETUSDT","APT-USD":"BINANCE:APTUSDT",
    "NEAR-USD":"BINANCE:NEARUSDT","ARB-USD":"BINANCE:ARBUSDT",
    "OP-USD":"BINANCE:OPUSDT","MKR-USD":"BINANCE:MKRUSDT",
    "GRT-USD":"BINANCE:GRTUSDT","AAVE-USD":"BINANCE:AAVEUSDT",
    "STX-USD":"BINANCE:STXUSDT","INJ-USD":"BINANCE:INJUSDT",
    "RUNE-USD":"BINANCE:RUNEUSDT","IMX-USD":"BINANCE:IMXUSDT",
    "FTM-USD":"BINANCE:FTMUSDT","SAND-USD":"BINANCE:SANDUSDT",
    "MANA-USD":"BINANCE:MANAUSDT","AXS-USD":"BINANCE:AXSUSDT",
    "THETA-USD":"BINANCE:THETAUSDT","EOS-USD":"BINANCE:EOSUSDT",
    "EGLD-USD":"BINANCE:EGLDUSDT","XMR-USD":"BINANCE:XMRUSDT",
    "ALGO-USD":"BINANCE:ALGOUSDT","FLOW-USD":"BINANCE:FLOWUSDT",
    "KCS-USD":"BINANCE:KCSUSDT","CHZ-USD":"BINANCE:CHZUSDT",
    "ZEC-USD":"BINANCE:ZECUSDT","DASH-USD":"BINANCE:DASHUSDT",
    "BAT-USD":"BINANCE:BATUSDT","ENJ-USD":"BINANCE:ENJUSDT",
}

SMA_KURZ    = 50
EMA_LANG    = 200
RSI_PERIODE = 14
RSI_SCHWELLE= 30
FETCH_DAYS  = EMA_LANG + 50
END_DATE    = datetime.today()
START_DATE  = END_DATE - timedelta(days=FETCH_DAYS)


# ════════════════════════════════════════════════════════════
#  ANALYSE-FUNKTIONEN (identisch mit Colab-Skript)
# ════════════════════════════════════════════════════════════
def tradingview_link(ticker: str) -> str:
    if ticker in TV_EXCHANGE:
        return f"https://www.tradingview.com/chart/?symbol={TV_EXCHANGE[ticker]}"
    return f"https://www.tradingview.com/symbols/{ticker}"


@st.cache_data(ttl=3600, show_spinner=False)
def lade_kursdaten(ticker: str) -> pd.DataFrame:
    df = yf.download(
        ticker,
        start=START_DATE.strftime("%Y-%m-%d"),
        end=END_DATE.strftime("%Y-%m-%d"),
        progress=False,
        auto_adjust=True,
    )
    if df.empty:
        return pd.DataFrame()
    df = df[["Close"]].copy()
    df.columns = ["Close"]
    df.dropna(inplace=True)
    return df


def berechne_indikatoren(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[f"SMA{SMA_KURZ}"]  = df["Close"].rolling(window=SMA_KURZ).mean()
    df[f"EMA{EMA_LANG}"]  = df["Close"].ewm(span=EMA_LANG, adjust=False).mean()
    delta   = df["Close"].diff()
    gewinn  = delta.clip(lower=0)
    verlust = -delta.clip(upper=0)
    avg_g   = gewinn.rolling(window=RSI_PERIODE, min_periods=RSI_PERIODE).mean()
    avg_v   = verlust.rolling(window=RSI_PERIODE, min_periods=RSI_PERIODE).mean()
    for i in range(RSI_PERIODE, len(df)):
        avg_g.iloc[i] = (avg_g.iloc[i-1] * (RSI_PERIODE-1) + gewinn.iloc[i])  / RSI_PERIODE
        avg_v.iloc[i] = (avg_v.iloc[i-1] * (RSI_PERIODE-1) + verlust.iloc[i]) / RSI_PERIODE
    rs = avg_g / avg_v.replace(0, float("inf"))
    df["RSI"] = 100 - (100 / (1 + rs))
    return df


def pruefe_signale(df: pd.DataFrame) -> dict:
    valid = df.dropna(subset=[f"EMA{EMA_LANG}", "RSI"])
    if len(valid) < 2:
        return {"rsi_signal": False, "ema_signal": False, "rsi": 99.0, "ema_abstand": None}
    heute    = valid.iloc[-1]
    gestern  = valid.iloc[-2]
    rsi_val      = float(heute["RSI"])
    kurs_heute   = float(heute["Close"])
    kurs_gestern = float(gestern["Close"])
    ema_heute    = float(heute[f"EMA{EMA_LANG}"])
    ema_gestern  = float(gestern[f"EMA{EMA_LANG}"])
    return {
        "rsi_signal":  rsi_val < RSI_SCHWELLE,
        "ema_signal":  (kurs_gestern < ema_gestern) and (kurs_heute >= ema_heute),
        "rsi":         rsi_val,
        "ema_abstand": (kurs_heute - ema_heute) / ema_heute * 100,
        "kurs":        kurs_heute,
    }


def golden_cross_status(df: pd.DataFrame) -> str:
    valid = df.dropna(subset=[f"SMA{SMA_KURZ}", f"EMA{EMA_LANG}"])
    if len(valid) < 2:
        return "—"
    a = valid.iloc[-1]
    v = valid.iloc[-2]
    sma_k = float(a[f"SMA{SMA_KURZ}"])
    ema_l = float(a[f"EMA{EMA_LANG}"])
    if sma_k > ema_l:
        return "Soeben" if float(v[f"SMA{SMA_KURZ}"]) <= float(v[f"EMA{EMA_LANG}"]) else "Aktiv"
    diff = (sma_k - ema_l) / ema_l * 100
    if diff >= -1.0:  return "Nahe"
    if diff >= -3.0:  return "Annäherung"
    return "—"


def erstelle_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    cutoff = df.index[-1] - pd.Timedelta(days=60)
    s = df[df.index >= cutoff].copy()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=s.index, y=s["Close"],
        fill='tozeroy', fillcolor='rgba(0,245,212,0.04)',
        line=dict(color='#00F5D4', width=1.8),
        name="Kurs", hovertemplate='%{y:,.4f}<extra></extra>'
    ))
    if f"SMA{SMA_KURZ}" in s and s[f"SMA{SMA_KURZ}"].notna().any():
        fig.add_trace(go.Scatter(
            x=s.index, y=s[f"SMA{SMA_KURZ}"],
            line=dict(color='#FF6B6B', width=1.4, dash='dot'),
            name=f"SMA {SMA_KURZ}", hovertemplate='%{y:,.4f}<extra></extra>'
        ))
    if f"EMA{EMA_LANG}" in s and s[f"EMA{EMA_LANG}"].notna().any():
        fig.add_trace(go.Scatter(
            x=s.index, y=s[f"EMA{EMA_LANG}"],
            line=dict(color='#00E676', width=1.4, dash='dash'),
            name=f"EMA {EMA_LANG}", hovertemplate='%{y:,.4f}<extra></extra>'
        ))
    fig.update_layout(
        paper_bgcolor='#0D1117', plot_bgcolor='#0D1117',
        font=dict(family='JetBrains Mono', color='#4A5568', size=11),
        margin=dict(l=0, r=0, t=36, b=0),
        title=dict(text=f"<b>{ticker}</b>  ·  60 Tage", font=dict(color='#EDF2F7', size=14)),
        legend=dict(
            bgcolor='rgba(0,0,0,0)', bordercolor='rgba(255,255,255,0.06)',
            borderwidth=1, font=dict(size=11)
        ),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)', zeroline=False, showline=False),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)', zeroline=False, showline=False),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#1A2035', bordercolor='#00F5D4',
                        font=dict(family='JetBrains Mono', color='#EDF2F7')),
    )
    return fig


# ════════════════════════════════════════════════════════════
#  SESSION STATE
# ════════════════════════════════════════════════════════════
if "scan_results"   not in st.session_state: st.session_state.scan_results   = []
if "last_scan_time" not in st.session_state: st.session_state.last_scan_time = None
if "scan_done"      not in st.session_state: st.session_state.scan_done      = False


# ════════════════════════════════════════════════════════════
#  SIDEBAR – Filter & Settings
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding:20px 0 16px 0; font-size:18px; font-weight:700;
                color:#EDF2F7; letter-spacing:-0.3px;'>
        ⚙ Einstellungen
    </div>
    """, unsafe_allow_html=True)

    scan_universe = st.multiselect(
        "Universe",
        options=["Top 50 Aktien", "Top 50 Krypto"],
        default=["Top 50 Aktien", "Top 50 Krypto"],
    )
    rsi_threshold = st.slider("RSI-Schwelle", min_value=20, max_value=50, value=30, step=1)
    zeige_nur_signale = st.toggle("Nur Signale anzeigen", value=True)

    st.markdown("<div style='height:1px;background:rgba(255,255,255,0.05);margin:20px 0'></div>",
                unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px;color:#2D3748;line-height:1.8'>
        Daten via Yahoo Finance<br>
        Indikatoren: RSI-14 · SMA-50 · EMA-200<br>
        Cache: 60 Min
  
