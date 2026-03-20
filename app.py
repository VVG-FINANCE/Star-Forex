import streamlit as st
import pandas as pd
from datetime import datetime

# Importações dos módulos internos (Garanta que os arquivos existem na pasta)
from config import Config
from data_manager import DataManager
from engine.core import TradingEngine

# 1. Configuração Estática da Página
st.set_page_config(
    page_title=f"{Config.APP_TITLE} - Estável",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS para cartões de métricas mais densos
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #f0f2f6; }
    [data-testid="stMetricDelta"] { font-size: 1rem; }
    div.stButton > button:first-child { background-color: #4CAF50; color:white; width: 100%; border-radius: 10px;}
    .reportview-container .main .block-container{ padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. Inicialização de Estado Singleton (Mantém os objetos vivos entre cliques)
if 'dm' not in st.session_state:
    st.session_state.dm = DataManager()
    st.session_state.engine = TradingEngine()
    st.session_state.last_run = None

# --- HEADER E BOTÃO DE ATUALIZAÇÃO ---
col_head, col_btn = st.columns([3, 1])

with col_head:
    st.title(f"📊 {Config.APP_TITLE}")
    if st.session_state.last_run:
        st.caption(f"Última análise gerada em: {st.session_state.last_run.strftime('%H:%M:%S')}")
    else:
        st.caption("Aguardando primeira execução.")

with col_btn:
    st.write("") # Espaçador
    # O botão engatilha a renderização completa da página (seguro e estável)
    run_analysis = st.button("🔄 Executar Nova Análise")

# --- FLUXO DE EXECUÇÃO CONTROLADO ---
# Só executa se o botão for clicado ou se for a primeira vez
if run_analysis or st.session_state.last_run is None:
    
    with st.spinner("Coletando dados da microestrutura do EUR/USD..."):
        # Coleta de Dados (Chamada síncrona, segura)
        df = st.session_state.dm.fetch_data()
        
    if df is not None:
        st.session_state.last_run = datetime.now()
        
        # Processamento pelo Core Engine
        opportunity, score = st.session_state.engine.process(df)
        
        current_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        delta_p = current_price - prev_price
        volatility = df['Close'].pct_change().std()

        # --- SEÇÃO 1: MÉTRICAS QUANTS PONTUAIS ---
        st.subheader("✅ Estado Atual do Mercado")
        c1, c2, c3, c4 = st.columns(4)
        
        c1.metric("Preço Atual", f"{current_price:.5f}", f"{delta_p:.5f}")
        
        # Cor do Score baseada na zona de decisão
        score_color = "normal"
        if score >= Config.SCORE_THRESHOLD_BUY or score <= Config.SCORE_THRESHOLD_SELL:
            score_color = "inverse" # Vermelho/Verde dependendo do delta
            
        c2.metric("Ensemble Score", f"{score}%", f"{score-50:.1f}% vs Neutro", delta_color=score_color)
        c3.metric("Volatilidade (1m)", f"{volatility*10000:.1f} Pips")
        
        # Filtro de Kalman vs Preço Real (Suavização)
        kalman_diff = current_price - df['Kalman_Price'].iloc[-1]
        c4.metric("Divergência Kalman", f"{kalman_diff:.5f}", help="Diferença entre preço real e o filtro de ruído.")

        st.divider()

        # --- SEÇÃO 2: OPORTUNIDADE ESTRUTURADA ---
        st.subheader("🎯 Oportunidade Detectada")
        
        if opportunity:
            with st.container(border=True):
                # Usando Markdown para controle total de cores e tamanhos na interface simples
                oc1, oc2 = st.columns([1, 2])
                
                with oc1:
                    st.markdown(f"""
                    <div style='background-color:{opportunity['color']}20; padding:20px; border-radius:10px; text-align:center;'>
                        <h1 style='color:{opportunity['color']}; margin:0;'>{opportunity['side']}</h1>
                        <h4 style='color:#f0f2f6; margin:5px 0 0 0;'>Score: {score}%</h4>
                    </div>
                    """, unsafe_allow_html=True)
                
                with oc2:
                    st.markdown("### Níveis Técnicos")
                    # Tabela Simples para níveis (Tabelas são leves e estáveis no React)
                    data = {
                        "Tipo de Ordem": ["Entrada Principal", "Entrada Secundária", "Stop Loss Principal", "Take Profit 1", "Take Profit 2"],
                        "Preço (EUR/USD)": [
                            f"**{opportunity['entry'][0]:.5f}**",
                            f"{opportunity['entry'][1]:.5f}",
                            f"<span style='color:{Config.COLORS['sell']}'>{opportunity['sl'][0]:.5f}</span>",
                            f"**{opportunity['tp'][0]:.5f}**",
                            f"{opportunity['tp'][1]:.5f}"
                        ]
                    }
                    levels_df = pd.DataFrame(data)
                    st.markdown(levels_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.warning("Modelos não convergiram. Score neutro. Nenhuma oportunidade estruturada recomendada no momento.")

        st.divider()

        # --- SEÇÃO 3: DADOS BRUTOS (Substitui o Gráfico Plotly pesado) ---
        with st.expander("Ver Tabela de Dados Recentes (Últimas 15 velas de 1m)"):
            # Exibir a tabela é infinitamente mais leve que renderizar o gráfico Candlestick Plotly
            display_df = df.tail(15)[['Open', 'High', 'Low', 'Close', 'Kalman_Price']].copy()
            # Formatação para 5 casas decimais
            st.dataframe(display_df.style.format("{:.5f}"), use_container_width=True)
            st.caption("Nota: O Filtro de Kalman é usado pelos modelos para detecção de tendência suavizada.")

    else:
        st.error("Falha crítica na coleta de dados da API Yahoo Finance. Tente novamente em alguns segundos.")

# --- FOOTER ESTÁTICO ---
st.write("")
st.caption(f"Parâmetros: Weights={Config.WEIGHTS} | Thresholds={Config.SCORE_THRESHOLD_BUY}/{Config.SCORE_THRESHOLD_SELL}")
