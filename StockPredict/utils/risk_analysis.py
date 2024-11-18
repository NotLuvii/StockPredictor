import numpy as np

def calculate_risk_metrics(returns):
    # Annualized volatility
    volatility = np.std(returns) * np.sqrt(252)
    # Sharpe Ratio (Assume risk-free rate = 0.02)
    risk_free_rate = 0.02
    sharpe_ratio = (np.mean(returns) - risk_free_rate) / volatility
    return {
        'volatility': round(volatility * 100, 2),
        'sharpe_ratio': round(sharpe_ratio, 2)
    }
