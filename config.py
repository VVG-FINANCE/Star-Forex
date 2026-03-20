import pandas as pd

class Config:
    # --- Configurações de Mercado ---
    SYMBOL = "EURUSD=X"
    PIP_ADJUSTMENT = 0.0001  # Ajuste manual para compensar delay/spread
    TIMEFRAME = "1m"         # Intervalo das velas
    WINDOW_LOOKBACK = 100    # Quantidade de velas para análise estatística
    
    # --- Configurações de Conexão Adaptativa ---
    INITIAL_INTERVAL = 5     # Começa tentando atualizar a cada 5 segundos
    MAX_INTERVAL = 60        # Se houver bloqueio, sobe até 60 segundos
    
    # --- Pesos do Score Probabilístico (Soma deve ser 100) ---
    # Estes pesos definem a influência de cada modelo no Score Final (0-100)
    WEIGHTS = {
        "price_action": 15,      # Candlesticks e Padrões
        "technical": 15,         # RSI, Médias, Bandas
        "institutional": 20,     # Zonas de Liquidez/Order Blocks
        "econophysics": 20,      # Hurst Exponent e Entropia
        "machine_learning": 20,  # Predição Random Forest
        "bayesian": 10           # Ajuste de probabilidade histórica
    }
    
    # --- Parâmetros de Machine Learning ---
    ML_TRAIN_SIZE = 500       # Quantidade de velas para treinamento inicial
    ML_ESTIMATORS = 100       # Quantidade de árvores no Random Forest
    
    # --- Interface e Design ---
    APP_TITLE = "EUR/USD Quant Analyzer"
    CHART_THEME = "plotly_dark"
    COLORS = {
        "buy": "#00FF7F",      # Verde Primavera
        "sell": "#FF4B4B",     # Vermelho Streamlit
        "neutral": "#31333F"   # Cinza Escuro
    }

    # --- Limites de Sinal ---
    SCORE_THRESHOLD_BUY = 65   # Score mínimo para sinal de Compra
    SCORE_THRESHOLD_SELL = 35  # Score máximo para sinal de Venda
