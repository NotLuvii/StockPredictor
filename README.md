# StockPredict: A Comprehensive Stock Management and Analysis App

## Overview
StockPredict is a web-based stock management and analysis application that allows users to:
- Manage their stock portfolio by adding, editing, and removing stocks.
- View stock price trends and historical data in an interactive graphical format.
- Perform risk analysis on their portfolio, including metrics such as volatility and Sharpe ratio.
- Convert the total portfolio worth into multiple currencies.
- Predict future stock prices using a machine learning model based on historical stock data.

## Features
### 1. **Portfolio Management**
- Add stocks to your portfolio with details such as ticker, quantity, and purchase price.
- Edit the quantity of stocks or remove stocks from your portfolio.
- View a table of all your portfolio stocks with real-time calculations of the total portfolio worth.

### 2. **Stock Viewing**
- Search for stocks and view their historical price data using interactive line graphs.
- Update timeframes dynamically (e.g., daily, monthly) to customize the displayed data.

### 3. **Currency Conversion**
- Convert your total portfolio worth into a variety of global currencies.
- Supported currencies include USD, EUR, GBP, INR, JPY, and more.

### 4. **Risk Analysis**
- Analyze the risk associated with your portfolio by calculating:
  - **Volatility**: A measure of price fluctuations over time.
  - **Sharpe Ratio**: A risk-adjusted measure of portfolio performance.
- Hover over tooltips to understand these metrics better.

### 5. **Stock Price Prediction**
- Predict future stock prices using a machine learning model that utilizes historical stock data.
- View prediction graphs for specific stocks directly on the Stock Viewing page.
- Access predictions in your portfolio for added stocks.

## Technologies Used
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python with Flask
- **Data Handling**: Pandas, NumPy, yFinance
- **Machine Learning**: Scikit-learn
- **Currency Conversion API**: forex-python
- **Graphs**: Chart.js
- **Deployment**: Flask development server
