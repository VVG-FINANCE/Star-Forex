import numpy as np
from scipy.stats import entropy

class QuantTools:
    @staticmethod
    def calculate_hurst(series):
        """
        Calcula o Expoente de Hurst (H).
        H < 0.5: Média reversiva (Anti-persistente)
        H = 0.5: Passeio aleatório (Random Walk)
        H > 0.5: Tendência (Persistente)
        """
        series = np.array(series)
        lags = range(2, 20)
        
        # Cálculo da Variância dos retornos para diferentes lags
        tau = [np.sqrt(np.std(np.subtract(series[lag:], series[:-lag]))) for lag in lags]
        
        # Regressão linear para encontrar a inclinação (Hurst)
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        
        # O coeficiente de Hurst é a inclinação * 2
        return poly[0] * 2.0

    @staticmethod
    def market_entropy(series, bins=10):
        """Mede a eficiência do mercado. Alta entropia = Ruído imprevisível."""
        hist, _ = np.histogram(series, bins=bins, density=True)
        return entropy(hist)

    @staticmethod
    def calculate_zscore(series):
        """Identifica anomalias estatísticas (extremos)."""
        return (series[-1] - np.mean(series)) / np.std(series)
