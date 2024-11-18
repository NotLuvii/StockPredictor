from flask import Blueprint, request, jsonify, render_template
import yfinance as yf
from utils.predictor import StockPredictor

stock_view_blueprint = Blueprint(
    'stock_viewing',
    __name__,
    template_folder='../../templates',
    static_folder='../../static'
)
predictor = StockPredictor()
@stock_view_blueprint.route('/')
def stock_view_home():
    return render_template('stock_view.html')

@stock_view_blueprint.route('/history', methods=['GET'])
def get_stock_history():
    ticker = request.args.get('ticker')
    period = request.args.get('period', '1mo')  # Default to 1 month

    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period)
        if data.empty:
            return jsonify({'error': f'No data found for ticker: {ticker}'}), 404

        history = data[['Open', 'High', 'Low', 'Close']].reset_index().to_dict(orient='records')
        return jsonify({'ticker': ticker, 'history': history})
    except Exception as e:
        return jsonify({'error': f'Unable to fetch data for ticker: {ticker}'}), 500


@stock_view_blueprint.route('/predict', methods=['GET'])
def predict_stock_price():
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({'error': 'Ticker symbol is required'}), 400

    try:
        # Fetch the most recent data for the ticker
        stock_data = yf.Ticker(ticker).history(period="5d")
        if stock_data.empty:
            return jsonify({'error': f'No data found for ticker: {ticker}'}), 404

        # Prepare the input for prediction
        recent_close = stock_data['Close'].iloc[-1]
        recent_return = stock_data['Close'].pct_change().iloc[-1]
        recent_volatility = stock_data['Close'].rolling(5).std().iloc[-1]
        
        input_data = [recent_close, recent_return, recent_volatility]
        predicted_price = predictor.predict(ticker, input_data)

        return jsonify({'ticker': ticker, 'predicted_price': predicted_price})
    except Exception as e:
        return jsonify({'error': str(e)}), 500