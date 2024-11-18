import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import numpy as np

class StockPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.trained_models = {}  # To cache models per ticker

    def train_model(self, ticker):
        """
        Train a predictive model for the given stock ticker.
        """
        try:
            data = yf.Ticker(ticker).history(period="1y")
            if data.empty:
                raise ValueError(f"No data available for ticker {ticker}")
            
            # Prepare data for training
            data['Return'] = data['Close'].pct_change().fillna(0)
            data['Volatility'] = data['Close'].rolling(5).std().fillna(0)
            data['Target'] = data['Close'].shift(-1)  # Next day's close price
            data = data.dropna()

            X = data[['Close', 'Return', 'Volatility']]
            y = data['Target']
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train the model
            self.model.fit(X_train, y_train)
            self.trained_models[ticker] = self.model

            # Validate the model
            predictions = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, predictions)
            print(f"Model trained for {ticker}, MAE: {mae:.2f}")

        except Exception as e:
            print(f"Error training model for {ticker}: {e}")

    def predict(self, ticker, recent_data):
        """
        Predict the next price based on recent data.
        """
        if ticker not in self.trained_models:
            self.train_model(ticker)  # Train model if not already trained

        try:
            model = self.trained_models[ticker]
            prediction = model.predict([recent_data])
            return prediction[0]
        except Exception as e:
            print(f"Error predicting for {ticker}: {e}")
            return None
