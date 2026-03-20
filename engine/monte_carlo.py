import numpy as np

class MonteCarloSimulator:
    def __init__(self, current_price, volatility, steps=60, simulations=1000):
        self.s0 = current_price
        self.vol = volatility
        self.steps = steps
        self.sims = simulations

    def simulate(self):
        """Gera caminhos aleatórios e calcula a probabilidade de fechamento positivo."""
        # dt = 1 minuto
        dt = 1 
        
        # Matriz de retornos aleatórios (Normal)
        # drift assumido como 0 para Forex intra-day (Brownian Motion Puro)
        daily_vol = self.vol / np.sqrt(dt) 
        
        # Geração de caminhos
        returns = np.random.normal(0, self.vol, (self.sims, self.steps))
        price_paths = self.s0 * np.exp(np.cumsum(returns, axis=1))
        
        final_prices = price_paths[:, -1]
        
        # Probabilidade de terminar acima do preço atual
        prob_up = np.mean(final_prices > self.s0)
        
        # Intervalo de Confiança 95%
        ci_low = np.percentile(final_prices, 2.5)
        ci_high = np.percentile(final_prices, 97.5)
        
        return {
            "prob_up": prob_up,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "mean_projection": np.mean(final_prices)
        }
