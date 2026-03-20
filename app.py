import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Importações dos nossos módulos internos
from config import Config
from data_manager import DataManager
from engine.core import TradingEngine

# 1. Configuração de Página e Estilo
st.set_page_config(
    page_title=Config.APP_TITLE,
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para esconder menus desnecessários e otimizar mobile
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialização de Estado (Singleton)
if 'dm' not in st.session_state:
    st.session_state.dm = DataManager()
    st.session_state.engine = TradingEngine()
    st.session_state.last_update = datetime.now()

# 3. Sidebar - Status e Configurações
with st.sidebar:
    st.title("🛡️ Sistema Quant")
    st.subheader("EUR/USD Real-Time")
    
    # Ajuste de Pip Dinâmico
    Config.PIP_ADJUSTMENT = st.number_input(
        "Ajuste de Pip (Offset)", 
        value=Config.PIP_ADJUSTMENT, 
        format="%.5f", 
        step=0.00001
    )
    
    st.divider()
    status = st.session_state.dm.get_market_status()
    st.write(f"**API Health:** {'✅ Estável' if status['is_healthy'] else '⚠️ Reconectando'}")
    st.write(f"**Refresh:** {status['interval']}s")
    st.write(f"**Última Sync:** {st.session_state.last_update.strftime('%H:%M:%S')}")

# 4. Layout Principal
col_price, col_score, col_trend = st.columns(3)

# --- FRAGMENTO DE ATUALIZAÇÃO ---
@st.fragment(run_every=Config.INITIAL_INTERVAL)
def main_loop():
    df = st.session_state.dm.fetch_data()
    
    if df is not None:
        st.session_state.last_update = datetime.now()
        
        # Processamento pelo Core Engine
        opportunity, score = st.session_state.engine.process(df)
        
        # A. Métricas de Topo
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        delta_p = current_price - prev_price
        
        with col_price:
            st.metric("Preço Atual", f"{current_price:.5f}", f"{delta_p:.5f}")
        
        with col_score:
            color = "normal" if 40 < score < 60 else "inverse"
            st.metric("Score Probabilístico", f"{score}%", f"{score-50:.1f}%", delta_color=color)
            
        with col_trend:
            trend_label = "Alta Volatilidade" if df['Close'].pct_change().std() > 0.0002 else "Baixa Volatilidade"
            st.metric("Regime de Mercado", trend_label)

        # B. Gráfico Interativo Plotly
        fig = go.Figure()
        
        # Candlesticks
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], 
            low=df['Low'], close=df['Close'], name="EUR/USD"
        ))
        
        # Kalman Filter Line
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Kalman_Price'], 
            line=dict(color='#00d4ff', width=1.5), name="Filtro de Kalman"
        ))
        
        fig.update_layout(
            template="plotly_dark", 
            height=450, 
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # C. Painel de Oportunidades
        if opportunity:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 2, 1])
                with c1:
                    st.markdown(f"### DIREÇÃO\n## <span style='color:{opportunity['color']}'>{opportunity['side']}</span>", unsafe_allow_html=True)
                with c2:
                    st.markdown("### NÍVEIS DE ENTRADA")
                    st.code(f"Principal: {opportunity['entry'][0]:.5f}\nSecundária: {opportunity['entry'][1]:.5f}")
                with c3:
                    st.markdown("### TAKE PROFIT (ALVOS)")
                    for i, tp in enumerate(opportunity['tp'], 1):
                        st.write(f"🎯 Alvo {i}: **{tp:.5f}**")
                    st.error(f"Stop Loss: {opportunity['sl'][0]:.5f}")
        else:
            st.info("🔎 Analisando microestrutura... Aguardando convergência de modelos.")

# Execução
main_loop()
