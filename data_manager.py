import yfinance as yf
import pandas as pd
import numpy as np
import time
from config import Config

class DataManager:
    def __init__(self):
        self.current_interval = Config.INITIAL_INTERVAL
        self.kf_state_estimate = None
        self.kf_error_estimate = 1.0
        self.consecutive_errors = 0

    def fetch_data(self):
        """
        Coleta dados do Yahoo Finance com sistema adaptativo de requisição.
        Implementa a lógica de backoff: 5s -> 10s -> 15s... se houver bloqueio.
        """
        try:
            # Download do par EUR/USD (Intervalo de 1 minuto para máxima precisão gratuita)
            df = yf.download(
                tickers=Config.SYMBOL, 
                period="1d", 
                interval="1m", 
                progress=False,
                timeout=10
            )
            
            if df.empty or len(df) < 10:
                raise ValueError("Dados insuficientes retornados pela API.")

            # Ajuste de Preço (Pip Adjustment configurável no config.py)
            df['Close'] = df['Close'] + Config.PIP_ADJUSTMENT
            df['High'] = df['High'] + Config.PIP_ADJUSTMENT
            df['Low'] = df['Low'] + Config.PIP_ADJUSTMENT
            
            # Aplicação do Filtro de Kalman no preço de fechamento
            df = self.apply_kalman_filter(df)
            
            # Reset do intervalo adaptativo em caso de sucesso
            self.current_interval = Config.INITIAL_INTERVAL
            self.consecutive_errors = 0
            
            return df

        except Exception as e:
            self.consecutive_errors += 1
            # Aumenta o intervalo progressivamente: 5, 10, 15, 20, 30, 60
            self.current_interval = min(self.current_interval + 5, Config.MAX_INTERVAL)
            print(f"Erro na coleta (Tentativa {self.consecutive_errors}): {e}. Novo intervalo: {self.current_interval}s")
            return None

    def apply_kalman_filter(self, df):
        """
        Algoritmo de Econofísica para redução de ruído gaussiano em séries temporais.
        """
        prices = df['Close'].values
        
        # Inicializa o estado se for a primeira execução
        if self.kf_state_estimate is None:
            self.kf_state_estimate = prices[0]

        kalman_prices = []
        Q = 1e-5  # Variância do Processo
        R = 0.0001 # Variância da Medição (Ruído da API)

        for z in prices:
            # Predição
            self.kf_error_estimate += Q
            
            # Atualização (Ganho de Kalman)
            kalman_gain = self.kf_error_estimate / (self.kf_error_estimate + R)
            self.kf_state_estimate = self.kf_state_estimate + kalman_gain * (z - self.kf_state_estimate)
            self.kf_error_estimate = (1 - kalman_gain) * self.kf_error_estimate
            
            kalman_prices.append(self.kf_state_estimate)

        df['Kalman_Price'] = kalman_prices
        return df

    def get_market_status(self):
        """Retorna metadados para o dashboard."""
        return {
            "interval": self.current_interval,
            "errors": self.consecutive_errors,
            "is_healthy": self.consecutive_errors == 0
        }
