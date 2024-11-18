from flask import Blueprint, render_template, request, jsonify, session
import yfinance as yf
from utils.currency_converter import convert_currency
from utils.risk_analysis import calculate_risk_metrics
import numpy as np
import requests
from utils.predictor import StockPredictor

portfolio_blueprint = Blueprint(
    'portfolio',
    __name__,
    template_folder='../../templates',
    static_folder='../../static'
)

predictor = StockPredictor()

# Ensure the portfolio key is always available in the session
@portfolio_blueprint.before_request
def initialize_portfolio():
    if 'portfolio' not in session:
        session['portfolio'] = []  # Initialize as an empty list

@portfolio_blueprint.route('/')
def portfolio_home():
    total_worth = sum(item['quantity'] * item['price'] for item in session['portfolio'])
    return render_template('portfolio.html', portfolio=session['portfolio'], total_worth=total_worth)

@portfolio_blueprint.route('/price', methods=['GET'])
def get_stock_price():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        if data.empty:
            return jsonify({'error': 'Invalid ticker symbol'}), 404

        price = data['Close'].iloc[-1]
        return jsonify({'ticker': ticker, 'price': float(price)})
    except Exception as e:
        return jsonify({'error': 'Unable to fetch stock price'}), 500

@portfolio_blueprint.route('/add', methods=['POST'])
def add_to_portfolio():
    data = request.json
    stock = data.get('stock')
    quantity = data.get('quantity')
    price = data.get('price')

    if not stock or not quantity or not price:
        return jsonify({'error': 'Invalid data'}), 400

    # Add to session
    portfolio = session['portfolio']
    portfolio.append({'stock': stock.upper(), 'quantity': quantity, 'price': price})
    session['portfolio'] = portfolio  # Update session
    session.modified = True

    return jsonify({'message': 'Stock added to portfolio'})

@portfolio_blueprint.route('/edit', methods=['POST'])
def edit_stock():
    data = request.json
    stock = data.get('stock')
    new_quantity = data.get('quantity')

    if not stock or new_quantity is None:
        return jsonify({'error': 'Invalid data'}), 400

    portfolio = session.get('portfolio', [])
    for item in portfolio:
        if item['stock'] == stock.upper():
            item['quantity'] = new_quantity
            session['portfolio'] = portfolio
            session.modified = True
            return jsonify({'message': 'Stock quantity updated successfully'})

    return jsonify({'error': 'Stock not found'}), 404


@portfolio_blueprint.route('/remove', methods=['POST'])
def remove_stock():
    data = request.json
    stock = data.get('stock')

    if not stock:
        return jsonify({'error': 'Invalid data'}), 400

    portfolio = session.get('portfolio', [])
    updated_portfolio = [item for item in portfolio if item['stock'] != stock.upper()]
    session['portfolio'] = updated_portfolio
    session.modified = True

    return jsonify({'message': 'Stock removed successfully'})

# Currency conversion endpoint
@portfolio_blueprint.route('/convert_currency', methods=['GET'])
def convert_currency():
    """
    Convert a given amount from one currency to another.
    """
    try:
        amount = float(request.args.get('amount'))
        from_currency = request.args.get('from_currency', 'USD')
        to_currency = request.args.get('to_currency', 'USD')

        # Ensure valid parameters
        if not amount or not from_currency or not to_currency:
            return jsonify({'error': 'Invalid parameters for currency conversion'}), 400

        # Perform the conversion using an external API
        api_url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(api_url)

        # Check for errors in the response
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch currency data'}), 500

        data = response.json()
        rates = data.get('rates', {})

        if to_currency not in rates:
            return jsonify({'error': f'Unsupported currency: {to_currency}'}), 400

        # Calculate converted amount
        converted_amount = amount * rates[to_currency]
        return jsonify({'converted_amount': converted_amount})
    
    except ValueError:
        return jsonify({'error': 'Invalid amount for conversion'}), 400
    except Exception as e:
        print(f"Error in convert_currency: {e}")  # Log the error for debugging
        return jsonify({'error': 'Internal server error during conversion'}), 500

@portfolio_blueprint.route('/set_conversion_state', methods=['POST'])
def set_conversion_state():
    data = request.json
    session['currency_state'] = data  # Save the selected currency and conversion result
    session.modified = True
    return jsonify({'message': 'Currency conversion state saved successfully'})

@portfolio_blueprint.route('/get_conversion_state', methods=['GET'])
def get_conversion_state():
    return jsonify(session.get('currency_state', {}))  # Return the saved state, if any



@portfolio_blueprint.route('/risk_analysis', methods=['GET'])
def risk_analysis():
    portfolio = session.get('portfolio', [])
    if not portfolio:
        return jsonify({'error': 'Portfolio is empty. Cannot perform risk analysis.'}), 400

    # Extract stocks and their quantities from the portfolio
    stocks = [item['stock'] for item in portfolio]
    quantities = np.array([item['quantity'] for item in portfolio])

    try:
        # Download historical stock prices
        stock_data = yf.download(stocks, period='1y')['Close']  # Get past 1 year's data
        stock_returns = stock_data.pct_change()  # Calculate daily returns

        # Normalize weights based on quantities
        weights = quantities / np.sum(quantities)

        # Calculate portfolio returns as a weighted sum of individual stock returns
        portfolio_returns = stock_returns.dot(weights)

        # Calculate risk metrics
        annualized_volatility = np.std(portfolio_returns) * np.sqrt(252)  # Annualized volatility
        sharpe_ratio = np.mean(portfolio_returns) / np.std(portfolio_returns)  # Assume risk-free rate = 0

        return jsonify({
            'volatility': round(annualized_volatility * 100, 2),  # As percentage
            'sharpe_ratio': round(sharpe_ratio, 2)
        })

    except Exception as e:
        return jsonify({'error': f'Risk analysis failed: {str(e)}'}), 500

@portfolio_blueprint.route('/set_risk_state', methods=['POST'])
def set_risk_state():
    data = request.json
    session['risk_state'] = data  # Save risk analysis results
    session.modified = True
    return jsonify({'message': 'Risk state saved successfully'})

@portfolio_blueprint.route('/get_risk_state', methods=['GET'])
def get_risk_state():
    return jsonify(session.get('risk_state', {}))  # Return the saved state, if any


@portfolio_blueprint.route('/predict_portfolio', methods=['GET'])
def predict_portfolio_prices():
    try:
        portfolio_predictions = []
        for item in session.get('portfolio', []):
            ticker = item['stock']
            stock_data = yf.Ticker(ticker).history(period="5d")
            if not stock_data.empty:
                recent_close = stock_data['Close'].iloc[-1]
                recent_return = stock_data['Close'].pct_change().iloc[-1]
                recent_volatility = stock_data['Close'].rolling(5).std().iloc[-1]

                input_data = [recent_close, recent_return, recent_volatility]
                predicted_price = predictor.predict(ticker, input_data)
                portfolio_predictions.append({
                    'stock': ticker,
                    'predicted_price': predicted_price
                })

        return jsonify({'predictions': portfolio_predictions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500