from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

class MLModule:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=7, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    def prepare_features(self, df):
        """Engenharia de recursos para o modelo de ML."""
        feat = pd.DataFrame(index=df.index)
        
        # Indicadores de Momentum e Volatilidade
        feat['returns'] = df['Close'].pct_change()
        feat['log_ret'] = np.log(df['Close'] / df['Close'].shift(1))
        feat['volatilidade'] = feat['returns'].rolling(10).std()
        
        # Distância de médias móveis (Mean Reversion)
        feat['dist_ema'] = df['Close'] - df['Close'].ewm(span=20).mean()
        
        # RSI Simples
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        feat['rsi'] = 100 - (100 / (1 + rs))

        # Target: 1 se o fechamento seguinte for maior que o atual
        target = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        return feat.fillna(0), target.fillna(0)

    def train(self, df):
        """Treina o modelo com os dados históricos disponíveis."""
        X, y = self.prepare_features(df)
        if len(X) < 100: return
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True

    def predict_proba(self, df):
        """Retorna a probabilidade de ALTA (0.0 a 1.0)."""
        if not self.is_trained: return 0.5
        X, _ = self.prepare_features(df)
        X_last = self.scaler.transform(X.tail(1))
        return self.model.predict_proba(X_last)[0][1]
