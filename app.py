# 4. Layout Principal - Reservando espaços fixos (Placeholders)
# Isso evita que o React tente remover nós que ainda estão sendo renderizados
metrics_container = st.container()
chart_placeholder = st.empty()
opp_placeholder = st.empty()

@st.fragment(run_every=10) # Aumentado para 10s para estabilidade no Cloud
def main_loop():
    df = st.session_state.dm.fetch_data()
    
    if df is not None:
        st.session_state.last_update = datetime.now()
        opportunity, score = st.session_state.engine.process(df)
        
        # A. Atualização de Métricas em Containers Fixos
        with metrics_container:
            col_price, col_score, col_trend = st.columns(3)
            current_price = df['Close'].iloc[-1]
            delta_p = current_price - df['Close'].iloc[-2]
            
            col_price.metric("Preço Atual", f"{current_price:.5f}", f"{delta_p:.5f}")
            col_score.metric("Score Probabilístico", f"{score}%", delta_color="normal" if 40 < score < 60 else "inverse")
            col_trend.metric("Regime", "Trending" if score > 60 or score < 40 else "Ranging")

        # B. Gráfico com KEY ÚNICA (Crucial para evitar o erro de removeChild)
        with chart_placeholder:
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], 
                low=df['Low'], close=df['Close'], name="EUR/USD"
            ))
            fig.add_trace(go.Scatter(
                x=df.index, y=df['Kalman_Price'], 
                line=dict(color='#00d4ff', width=1.5), name="Kalman"
            ))
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
            
            # O parâmetro 'key' garante que o React rastreie o gráfico corretamente
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False}, key="forex_main_chart")

        # C. Painel de Oportunidades em Placeholder Fixo
        with opp_placeholder:
            if opportunity:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 2, 1])
                    c1.markdown(f"### <span style='color:{opportunity['color']}'>{opportunity['side']}</span>", unsafe_allow_html=True)
                    c2.code(f"Entrada: {opportunity['entry'][0]:.5f}\nSL: {opportunity['sl'][0]:.5f}")
                    c3.write(f"Alvo 1: {opportunity['tp'][0]:.5f}")
            else:
                st.info("🔎 Monitorando fluxo institucional... Aguardando convergência.")

# Execução do loop estável
main_loop()
