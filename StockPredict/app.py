import os
from flask import Flask, render_template
from features.portfolio.portfolio import portfolio_blueprint
from features.stock_viewing.stock_viewing import stock_view_blueprint

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = os.urandom(24)

# Register blueprints
app.register_blueprint(portfolio_blueprint, url_prefix='/portfolio')
app.register_blueprint(stock_view_blueprint, url_prefix='/stock')

@app.route('/')
def home():
    return render_template('base.html', title="Stock Viewing")

if __name__ == '__main__':
    app.run(debug=True)
