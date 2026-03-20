import numpy as np

class InstitutionalTools:
    @staticmethod
    def detect_liquidity_zones(df):
        """
        Detecta Order Blocks e clusters de liquidez.
        Baseia-se nos pontos onde o mercado 'parou' e reverteu com força.
        """
        lookback = 30
        highs = df['High'].rolling(window=lookback).max()
        lows = df['Low'].rolling(window=lookback).min()
        
        resistance = highs.iloc[-1]
        support = lows.iloc[-1]
        
        return support, resistance

    @staticmethod
    def price_acceleration(df):
        """
        Mede a força institucional. 
        Aceleração positiva forte indica entrada de volume comprador pesado.
        """
        returns = df['Close'].pct_change()
        # Derivada segunda do preço (taxa de variação da velocidade)
        acceleration = returns.diff()
        return acceleration.iloc[-1]

    @staticmethod
    def detect_fvg(df):
        """
        Detecta Fair Value Gaps (Desequilíbrio de Preço).
        Ocorre quando o mercado se move tão rápido que deixa 'buracos' de liquidez.
        """
        # Simplificação: detecta gaps entre o High de t-2 e Low de t
        last_three = df.tail(3)
        if len(last_three) < 3: return False
        
        # Gap de Alta (Bullish FVG)
        if last_three['Low'].iloc[-1] > last_three['High'].iloc[-3]:
            return True
        return False
