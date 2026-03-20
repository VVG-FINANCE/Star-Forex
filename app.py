import streamlit as st
import pandas as pd
from datetime import datetime

# Importações dos módulos internos
from config import Config
from data_manager import DataManager
from engine.core import TradingEngine

# 1. Configuração de Página (Estática e Robusta)
st.set_page_config(page_title=Config.APP_TITLE, layout="wide")

# 2. Inicialização de Estado com Segurança
if 'dm' not in st.session_state:
    st.session_state.dm = DataManager()
    st.session_state.engine = TradingEngine()
    st.session_state.run_count = 0 # Contador para gerar KEYS ÚNICAS

# 3. Cabeçalho Fixo
st.title(f"📊 {Config.APP_TITLE}")

# Placeholder mestre: É a ÚNICA "caixa" que o Streamlit vai manipular
# Isso evita o erro de removeChild em múltiplos nós
main_placeholder = st.empty()

# 4. Loop de Atualização Protegido
# Aumentamos o tempo para 15s para garantir que o DOM termine de respirar
@st.fragment(run_every=15)
def stable_runtime():
    st.session_state.run_count += 1
    # Criamos um sufixo de KEY único para cada ciclo
    ctx_key = f"loop_{st.session_state.run_count}"
    
    df = st.session_state.dm.fetch_data()
    
    with main_placeholder.container():
        if df is not None:
            opportunity, score = st.session_state.engine.process(df)
            
            # Layout em Colunas (Dentro do container estável)
            c1, c2, c3 = st.columns(3)
            
            # Usamos keys dinâmicas baseadas no contador de ciclo
            c1.metric("Preço EUR/USD", f"{df['Close'].iloc[-1]:.5f}", key=f"price_{ctx_key}")
            c2.metric("Probabilidade Score", f"{score}%", key=f"score_{ctx_key}")
            c3.metric("Status API", "Conectado", key=f"status_{ctx_key}")
            
            st.divider()
            
            # Painel de Oportunidade com ID Único
            if opportunity:
                st.subheader(f"🎯 Sinal Detectado", anchor=False)
                with st.container(border=True):
                    col_side, col_data = st.columns([1, 2])
                    col_side.markdown(f"## {opportunity['side']}")
                    col_data.json(opportunity)
            else:
                st.info("Aguardando convergência dos modelos matemáticos...", icon="🔎")
                
            # Tabela de dados (Mais estável que gráfico em conexões lentas)
            with st.expander("Ver Microestrutura de Preços", expanded=False):
                st.dataframe(df.tail(10), use_container_width=True, key=f"table_{ctx_key}")

        else:
            st.error("Erro de conexão com o provedor de dados. Tentando reconectar...")

# Executa o loop
stable_runtime()
