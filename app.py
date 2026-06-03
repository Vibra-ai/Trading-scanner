import streamlit as st
import pandas as pd
import requests

# ── APP-KONFIGURATION ───────────────────────────────────────
st.set_page_config(page_title="Trading Scanner Pro", layout="wide", page_icon="📈")
st.title("📈 Trading Scanner Pro (Cloud Version)")
st.write("Professionelle und stabile Marktanalyse direkt über globale Cloud-Server.")

# Die stabilsten Krypto-Handelspaare 
TOP_KRYPTO = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", 
    "XRPUSDT", "ADAUSDT", "LINKUSDT", "LTCUSDT"
]

# Parameter-Sidebar
st.sidebar.header("⚙️ Scanner Einstellungen")
rsi_schwelle = st.sidebar.slider("RSI Überverkauft-Schwelle", 10, 40, 30)

def get_tradingview_link(ticker):
    return f"https://www.tradingview.com/symbols/{ticker}/"

def hole_krypto_daten(symbol):
    """Holt historische Kerzen-Daten über den unblockierbaren US-Server."""
    # Wechsel auf die unblockierte API-Variante
    url = f"https://api.binance.us/api/v3/klines?symbol={symbol}&interval=1d&limit=250"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return None
        daten = res.json()
        closes = [float(kerze[4]) for kerze in daten]
        df = pd.DataFrame(closes, columns=["Close"])
        
        # EMA 200 Berechnung
        df["EMA200"] = df["Close"].ewm(span=200, adjust=False).mean()
        
        # RSI 14 Berechnung
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

# ── SCANNER STARTEN ─────────────────────────────────────────
if st.button("🚀 Markt-Scan jetzt starten", use_container_width=True):
    st.info("Verbinde mit Daten-Servern... Bitte einen Moment Geduld...")
    fortschritt = st.progress(0)
    ergebnisse = []
    
    for idx, ticker in enumerate(TOP_KRYPTO):
        daten = hole_krypto_daten(ticker)
        if daten is not None and len(daten) == 2:
            heute = daten.iloc[-1]
            gestern = daten.iloc[-2]
            
            rsi_aktuell = float(heute["RSI"])
            kurs_heute = float(heute["Close"])
            kurs_gestern = float(gestern["Close"])
            ema_heute = float(heute["EMA200"])
            ema_gestern = float(gestern["EMA200"])
            
            rsi_sig = "🔴 ÜBERVERKAUFT" if rsi_aktuell < rsi_schwelle else "⚪ Normal"
            ema_sig = "🟢 AUSBRUCH" if (kurs_gestern < ema_gestern and kurs_heute >= ema_heute) else "⚪ Kein Signal"
            
            ergebnisse.append({
                "Asset": ticker.replace("USDT", " / USDT"),
                "Aktueller Preis": f"{kurs_heute:,.2f} $",
                "RSI (14)": f"{rsi_aktuell:.1f}",
                "RSI Status": rsi_sig,
                "EMA200 Trend": ema_sig,
                "Link": get_tradingview_link(ticker)
            })
        fortschritt.progress((idx + 1) / len(TOP_KRYPTO))
        
    if ergebnisse:
        df_res = pd.DataFrame(ergebnisse)
        st.success(f"💥 Scan erfolgreich abgeschlossen! {len(df_res)} Märkte analysiert.")
        
        # Interaktiver Filter
        nur_treffer = st.checkbox("Nur aktive Signale einblenden")
        if nur_treffer:
            df_res = df_res[(df_res["RSI Status"] == "🔴 ÜBERVERKAUFT") | (df_res["EMA200 Trend"] == "🟢 AUSBRUCH")]
        
        # Schicke Tabelle anzeigen
        st.dataframe(df_res[["Asset", "Aktueller Preis", "RSI (14)", "RSI Status", "EMA200 Trend"]], use_container_width=True)
        
        # Direkt-Links als Buttons
        st.write("### 📊 TradingView Charts öffnen:")
        cols = st.columns(4)
        for i, row in enumerate(ergebnisse):
            with cols[i % 4]:
                st.link_button(f"🔍 {row['Asset']}", row['Link'], use_container_width=True)
    else:
        st.error("Der Server konnte keine Verbindung aufbauen. Bitte warte einen Moment und klicke erneut auf Scannen.")
