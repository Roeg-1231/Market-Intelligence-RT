import sys
import os
# Reload cache 3
import streamlit as st
import pandas as pd
import altair as alt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.queries import fetch_all_processed_news, fetch_sentiment_summary, fetch_financial_metrics, fetch_accuracy

st.set_page_config(page_title="Market Intelligence RT", page_icon="📈", layout="wide")

st.markdown("""
<style>
    .main-title {
        color: #0bd47a; 
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .metric-caption {
        font-size: 0.8rem;
        color: #a1a1aa;
        margin-top: -15px;
        margin-bottom: 15px;
    }
    .stMetric {
        background-color: #1e1e2e;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #313244;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">📈 Mercado Inteligente RT </h1>', unsafe_allow_html=True)
st.write("Dashboard Profesional impulsado por IA Financiera (FinBERT + OHLC Valuation).")

from src.processing.analyst import MarketAnalyst

try:
    df_news = fetch_all_processed_news()
    df_sentiment = fetch_sentiment_summary()
    df_prices = fetch_financial_metrics()
    ia_accuracy = fetch_accuracy()
    
    # Cargar The Analyst LLM
    analyst = MarketAnalyst()
    executive_summary = analyst.generate_executive_summary(df_news)
except Exception as e:
    st.error(f"Error Database u Orquestador: {e}")
    st.stop()

if df_news.empty:
    st.warning("No hay registros. Ejecute el ETL Backend primero (`run_processing.py`).")
    st.stop()

# ==== THE ANALYST (EXECUTIVE SUMMARY) ====
st.markdown("### 🤖 The Analyst (Resumen Ejecutivo)")
st.info(executive_summary)
st.divider()

# ==== FILA 1: KPIs ====
st.markdown("### Métricas Generales")
c1, c2, c3, c4 = st.columns(4)

total_news = len(df_news)
try:
    dom_sent = df_sentiment.sort_values(by="cantidad", ascending=False).iloc[0]
    label_dom = str(dom_sent['sentimiento']).capitalize()
    pct_dom = (dom_sent['cantidad'] / total_news) * 100
except:
    label_dom, pct_dom = "N/A", 0

score_avg = df_news['confianza'].mean() * 100 if 'confianza' in df_news.columns else 0

c1.metric("Volumen Textual", f"{total_news} Noticias", help="Cantidad total de noticias que la IA ha leído y procesado hoy.")
st.markdown('<p class="metric-caption">Total de datos leídos</p>', unsafe_allow_html=True)

c2.metric("Tendencia Clave", f"{label_dom}", f"{pct_dom:.1f}%", help="Es el sentimiento que más se repite en las noticias actuales.")
st.markdown(f'<p class="metric-caption">Sentimiento más frecuente</p>', unsafe_allow_html=True)

c3.metric("Seguridad IA", f"{score_avg:.1f}%", help="Certeza promedio del modelo FinBERT. Solo noticias con >90% se consideran para el éxito real.")
st.markdown('<p class="metric-caption">Nivel de certeza del modelo</p>', unsafe_allow_html=True)

c4.metric(label="✅ Éxito Real (Pro)", value=f"{ia_accuracy:.1f} %", delta="Precisión", delta_color="normal", help="Coincidencias de noticias de ALTA CONFIANZA (>90%) con el movimiento del Nasdaq (QQQ) 4 horas después.")
st.markdown('<p class="metric-caption">Aciertos T+4h (Señal >0.90)</p>', unsafe_allow_html=True)
st.divider()

# ==== FILA 2: GRÁFICAS ====
st.markdown("### Backtest Visual: IA contra Realidad")
chart_c1, chart_c2 = st.columns([1, 2.5])

with chart_c1:
    st.markdown("##### Estructura de Emociones")
    donut = alt.Chart(df_sentiment).mark_arc(innerRadius=65).encode(
        theta=alt.Theta(field="cantidad", type="quantitative"),
        color=alt.Color(field="sentimiento", type="nominal", scale=alt.Scale(
            domain=['positive', 'neutral', 'negative'],
            range=['#0bd47a', '#737373', '#ff4b4b']
        )),
    ).properties(height=350)
    st.altair_chart(donut, use_container_width=True)

with chart_c2:
    st.markdown("##### Dinámica Intradía: Sentimiento vs Nasdaq (QQQ)")
    # Data prep
    df_bar = df_news.copy()
    df_bar['fecha_corta'] = pd.to_datetime(df_bar['fecha']).dt.strftime('%Y-%m-%d')
    df_grouped = df_bar.groupby(['fecha_corta', 'sentimiento']).size().reset_index(name='qty')
    
    if not df_prices.empty:
        df_p = df_prices.copy()
        df_p['fecha_corta'] = pd.to_datetime(df_p['fecha']).dt.strftime('%Y-%m-%d')
        # Limpiar fin de semanas agrupando precio por día
        df_p = df_p.groupby('fecha_corta').last().reset_index()
        
        df_merged = pd.merge(df_grouped, df_p, on='fecha_corta', how='left')
        
        base = alt.Chart(df_merged).encode(x=alt.X('fecha_corta:T', title="Cronología (Días)"))
        
        bar = base.mark_bar(opacity=0.6).encode(
            y=alt.Y('qty:Q', title="Cantidad de Noticias"),
            color=alt.Color('sentimiento:N', scale=alt.Scale(domain=['positive', 'neutral', 'negative'], range=['#0bd47a', '#737373', '#ff4b4b']), title="Sentimiento"),
            tooltip=[alt.Tooltip('fecha_corta:T', title="Fecha"), alt.Tooltip('qty:Q', title="Noticias"), alt.Tooltip('sentimiento:N', title="Tipo")]
        )
        
        line = base.mark_line(color='#00d1ff', strokeWidth=5, interpolate='monotone').encode(
            y=alt.Y('close_price:Q', title="Precio QQQ (USD)", scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip('fecha_corta:T', title="Fecha/Hora"), alt.Tooltip('close_price:Q', title="Precio Cierre", format="$,.2f")]
        )
        
        # Añadir puntos a la línea para que sea más visible en días específicos
        points = base.mark_point(color='#00d1ff', size=100, filled=True).encode(
            y=alt.Y('close_price:Q'),
            tooltip=[alt.Tooltip('fecha_corta:T', title="Fecha/Hora"), alt.Tooltip('close_price:Q', title="Precio", format="$,.2f")]
        )
        
        dual_chart = alt.layer(bar, line, points).resolve_scale(y='independent').properties(height=400)
        st.altair_chart(dual_chart, use_container_width=True)
        st.caption("💡 **Ayuda:** Las barras muestran el volumen de noticias. La línea azul muestra el precio del Nasdaq (QQQ). Éxito Real calculado a T+4h para señales > 0.90.")
    else:
        st.info("No hay datos históricos bursátiles disponibles para el Doble Eje.")

st.divider()

# ==== FILA 3: TABLA INTERACTIVA ====
st.markdown("### Extracción Transversal (Market Log)")
st.dataframe(
    df_news[['fecha', 'sentimiento', 'market_validated', 'confianza', 'razonamiento', 'titulo']],
    use_container_width=True,
    hide_index=True,
    column_config={
        "fecha": st.column_config.DatetimeColumn("Fecha"),
        "sentimiento": st.column_config.TextColumn("Sentimiento", width="small"),
        "market_validated": st.column_config.CheckboxColumn("Validado"),
        "confianza": st.column_config.NumberColumn("Certeza", format="%.2f"),
        "razonamiento": st.column_config.TextColumn("Motivo de la IA", width="medium"),
        "titulo": st.column_config.TextColumn("Titular Financiero", width="large")
    }
)
