import streamlit as st
import pandas as pd
import requests

# ── APP-KONFIGURATION & PREMIUM STYLING ───────────────────────────────────────
st.set_page_config(
    page_title="Vibra Analytics | Trading Terminal", 
    layout="wide", 
    page_icon="⚡"
)

# Custom CSS für professionelles FinTech-Design (Dark-Theme Optimierung)
st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .stDeployButton { display:none; } 
    footer { visibility: hidden; }
    
    /* Ticker Styling */
    .ticker-wrap { width: 100%; background: #111; padding: 8px 0; border-radius: 6px; margin-bottom: 20px; border: 1px solid #222; }
    .ticker-text { font-family: monospace; font-size: 14px; color: #00ffcc; text-align: center; font-weight: bold; }
    
    /* Metric Cards Tuning */
    div[data-testid="stMetricValue"] { font-size: 32px; font-weight: bold; color: #00ffcc; }
    div[data-testid="stMetricLabel"] { font-size: 14px; color: #888; }
    </style>
""", unsafe_allow_html=True)

# ── DATEN-Schnittstellen ──────────────────────────────────────────────────────
MÄRKTE = {
    "BTC": "Bitcoin", "ETH": "Ethereum", "BNB": "Binance Coin", 
    "SOL": "Solana", "XRP": "Ripple", "ADA": "Cardano", 
    "LINK": "Chainlink", "LTC": "Litecoin", "DOT": "Polkadot", "AVAX": "Avalanche"
}

def hole_ticker_preise():
    """Holt super schnelle Live-Preise für das obere Banner."""
    url = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,BNB,SOL&tsyms=USD"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            p = res.json()
            return f"🔥 LIVE TICKER ── ₿ BTC: ${p['BTC']['USD']:,}  |  Ξ ETH: ${p['ETH']['USD']:,}  |  🔶 BNB: ${p['BNB']['USD']:,}  |  ☀️ SOL: ${p['SOL']['USD']:,}"
    except:
        pass
    return "⚡ Vibra Analytics Terminal Live Market Feed"

def hole_fear_and_greed():
    """Holt den aktuellen Krypto Fear & Greed Index."""
    try:
        res = requests.get("https://api.alternative.me/fng/", timeout=5)
        if res.status_code == 200:
            daten = res.json()
            val = daten["data"][0]["value"]
            class_val = daten["data"][0]["value_classification"]
            return f"{val} ({class_val})"
    except:
        pass
    return "50 (Neutral)"

def hole_historische_daten(coin_ticker):
    url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym={coin_ticker}&tsym=USD&limit=250"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200: return None
        daten = res.json()
        kerzen = daten.get("Data", {}).get("Data", [])
        if not kerzen: return None
            
        closes = [float(k["close"]) for k in kerzen]
        df = pd.DataFrame(closes, columns=["Close"])
        df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()
        
        delta = df["Close"].diff()
        gewinn = delta.clip(lower=0)
        verlust = -delta.clip(upper=0)
        avg_g = gewinn.rolling(window=14).mean().to_numpy()
        avg_v = verlust.rolling(window=14).mean().to_numpy()
        
        for i in range(14, len(df)):
            avg_g[i] = (avg_g[i-1] * 13 + gewinn.to_numpy()[i]) / 14
            avg_v[i] = (avg_v[i-1] * 13 + verlust.to_numpy()[i]) / 14
            
        df["RSI"] = 100 - (100 / (1 + (avg_g / pd.Series(avg_v).replace(0, float("inf")).to_numpy())))
        return df.dropna().iloc[-2:]
    except:
        return None

# ── OBERES LIVE BANNER ────────────────────────────────────────────────────────
ticker_string = hole_ticker_preise()
st.markdown(f'<div class="ticker-wrap"><div class="ticker-text">{ticker_string}</div></div>', unsafe_allow_html=True)

# Titel-Zeile
col_title, col_fng = st.columns([3, 1])
with col_title:
    st.title("⚡ Vibra Premium Terminal")
    st.caption("Institutioneller Cloud-Scanner für mathematische Krypto-Einstiege")
with col_fng:
    fng_status = hole_fear_and_greed()
    st.metric("📊 Markt-Sentiment", fng_status)

st.markdown("---")

# ── SIDEBAR CONTROL PANEL ─────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/nolan/96/dashboard.png", width=70)
st.sidebar.title("Terminal Steuerung")

# Neuer Premium-Filter
signal_filter = st.sidebar.selectbox(
    "🎯 Signal-Filterung",
    ["Alle Coins anzeigen", "Nur aktive RSI Kaufsignale", "Nur EMA200 Ausbrüche", "Alle aktiven Signale"]
)

rsi_schwelle = st.sidebar.slider("🔥 RSI Überverkauft-Grenze", 15, 40, 30)

st.sidebar.markdown("---")
st.sidebar.markdown("### Systemstatus")
st.sidebar.success("🟢 Cloud-Server: Aktiv")
st.sidebar.success("🟢 Datenfeed: Verbunden")

# ── LOGIK & DETEKTION ─────────────────────────────────────────────────────────
if st.button("🚀 Globalen Markt-Scan starten", use_container_width=True):
    with st.spinner("Frage globale Orderbücher ab und kalkuliere Algorithmen..."):
        ergebnisse = []
        rsi_count = 0
        ema_count = 0
        
        for ticker, name in MÄRKTE.items():
            daten = hole_historische_daten(ticker)
            if daten is not None and len(daten) == 2:
                heute = daten.iloc[-1]
                gestern = daten.iloc[-2]
                
                rsi_aktuell = float(heute["RSI"])
                kurs_heute = float(heute["Close"])
                kurs_gestern = float(gestern["Close"])
                ema_heute = float(heute["EMA200"])
                ema_gestern = float(gestern["EMA200"])
                
                # Signal-Klassifizierung
                is_rsi_signal = rsi_aktuell < rsi_schwelle
                is_ema_signal = (kurs_gestern < ema_gestern and kurs_heute >= ema_heute)
                
                rsi_status = "🚨 ÜBERVERKAUFT (Kaufzone)" if is_rsi_signal else "🟢 Normal"
                ema_status = "🚀 BULLISH BREAKOUT" if is_ema_signal else "⚪ Trendlos"
                
                if is_rsi_signal: rsi_count += 1
                if is_ema_signal: ema_count += 1
                
                # Filtern nach Auswahl in Sidebar
                if signal_filter == "Nur aktive RSI Kaufsignale" and not is_rsi_signal: continue
                if signal_filter == "Nur EMA200 Ausbrüche" and not is_ema_signal: continue
                if signal_filter == "Alle aktiven Signale" and not (is_rsi_signal or is_ema_signal): continue
                
                ergebnisse.append({
                    "Asset": f"{name} ({ticker})",
                    "Preis": f"${kurs_heute:,.2f}",
                    "RSI (14)": round(rsi_aktuell, 1),
                    "RSI Status": rsi_status,
                    "EMA200 Trend": ema_status,
                    "Link": f"https://www.tradingview.com/symbols/{ticker}USDT/"
                })
        
        # Dashboard-Metriken anzeigen
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Märkte analysiert", f"{len(MÄRKTE)} Coins")
        with m2: st.metric("Erkannte RSI-Signale", f"{rsi_count} Treffer", delta=rsi_count if rsi_count > 0 else None)
        with m3: st.metric("EMA200 Ausbrüche", f"{ema_count} Treffer", delta=ema_count if i_ema_signal else None, delta_color="inverse")
        
        st.write("###")
        
        if ergebnisse:
            tab_matrix, tab_charts = st.tabs(["📋 Professionelle Signal-Matrix", "📈 TradingView Terminal"])
            
            with tab_matrix:
                df_res = pd.DataFrame(ergebnisse)
                
                # High-End Tabellen-Styling mit Pandas Styler (Farbige Highlights)
                def style_signale(val):
                    if "🚨" in str(val): return 'background-color: rgba(255, 75, 75, 0.2); color: #ff4b4b; font-weight: bold;'
                    if "🚀" in str(val): return 'background-color: rgba(9, 171, 92, 0.2); color: #09ab5c; font-weight: bold;'
                    return ''
                
                styled_df = df_res[["Asset", "Preis", "RSI (14)", "RSI Status", "EMA200 Trend"]].style.applymap(
                    style_signale, subset=["RSI Status", "EMA200 Trend"]
                )
                
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
            with tab_charts:
                st.write("Schnellzugriff auf Krypto-Charts:")
                grid = st.columns(4)
                for idx, row in enumerate(ergebnisse):
                    with grid[idx % 4]:
                        btn_label = f"📈 {row['Asset']}"
                        if "🚨" in row["RSI Status"] or "🚀" in row["EMA200 Trend"]:
                            btn_label = f"⚡ SIGNAL: {row['Asset']}"
                        st.link_button(btn_label, row["Link"], use_container_width=True)
        else:
            st.warning("Keine Coins entsprechen deinen aktuellen Filterkriterien. Passe die Filter an und scanne erneut.")
    
