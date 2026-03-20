import numpy as np
import pandas as pd
from config import Config
from engine.ml_module import MLModule
from engine.quantitative_tools import QuantTools
from engine.institutional_tools import InstitutionalTools
from engine.monte_carlo import MonteCarloSimulator

class TradingEngine:
    def __init__(self):
        self.ml = MLModule()
        self.tools = QuantTools()
        self.inst = InstitutionalTools()
        self.is_ready = False

    def process(self, df):
        """
        Executa o pipeline analítico completo e retorna o Score + Oportunidade.
        """
        if len(df) < Config.WINDOW_LOOKBACK:
            return None, 0

        # 1. Preparação de Dados e Treino de ML (Se necessário)
        if not self.ml.is_trained:
            self.ml.train(df)

        # 2. Coleta de sinais das Camadas Analíticas
        current_price = df['Close'].iloc[-1]
        volatility = df['Close'].pct_change().std()
        
        # Camada 1: Machine Learning (Direção Probabilística)
        ml_prob = self.ml.predict_proba(df)
        
        # Camada 2: Econofísica (Regime de Mercado via Hurst)
        h_exponent = self.tools.calculate_hurst(df['Close'].tail(Config.WINDOW_LOOKBACK))
        # H > 0.5 indica tendência, H < 0.5 indica reversão à média
        
        # Camada 3: Monte Carlo (Simulação de Alvos)
        mc = MonteCarloSimulator(current_price, volatility)
        mc_results = mc.simulate()
        
        # Camada 4: Institucional (Zonas de Liquidez)
        support, resistance = self.inst.detect_liquidity_zones(df)

        # 3. Cálculo do Ensemble Score (Ponderado pelo Config.WEIGHTS)
        final_score = self._calculate_ensemble_score(
            ml_prob, h_exponent, mc_results['prob_up'], current_price, support, resistance
        )

        # 4. Estruturação da Oportunidade
        opportunity = self._build_opportunity(current_price, final_score, volatility)

        return opportunity, round(final_score, 2)

    def _calculate_ensemble_score(self, ml_p, hurst, mc_p, price, sup, res):
        """Consolida os pesos definidos no config.py"""
        w = Config.WEIGHTS
        
        # Score ML (0-100)
        s_ml = ml_p * 100
        
        # Score Econofísica (Baseado no Hurst e direção do preço)
        # Se H > 0.55 e preço subindo, score alto.
        s_econo = 70 if (hurst > 0.52) else 40
        
        # Score Institucional (Proximidade de zonas de liquidez)
        dist_sup = abs(price - sup)
        dist_res = abs(price - res)
        s_inst = 80 if dist_sup < dist_res else 20
        
        # Média Ponderada
        score = (
            (s_ml * (w['machine_learning']/100)) +
            (mc_p * 100 * (w['econophysics']/50)) + # MC entra como peso de probabilidade
            (s_inst * (w['institutional']/100)) +
            (s_econo * (w['econophysics']/50))
        )
        return min(max(score, 0), 100) # Clamp entre 0 e 100

    def _build_opportunity(self, price, score, vol):
        """Define os níveis de Trade baseados na volatilidade real (ATR-like)."""
        atr_simulado = price * (vol * 2) # Usa volatilidade para definir stop
        
        if score >= Config.SCORE_THRESHOLD_BUY:
            return {
                "side": "COMPRA (LONG)",
                "entry": [price, price - (atr_simulado * 0.5)],
                "sl": [price - (atr_simulado * 1.5)],
                "tp": [price + (atr_simulado * 2), price + (atr_simulado * 4)],
                "color": Config.COLORS["buy"]
            }
        elif score <= Config.SCORE_THRESHOLD_SELL:
            return {
                "side": "VENDA (SHORT)",
                "entry": [price, price + (atr_simulado * 0.5)],
                "sl": [price + (atr_simulado * 1.5)],
                "tp": [price - (atr_simulado * 2), price - (atr_simulado * 4)],
                "color": Config.COLORS["sell"]
            }
        return None
