from forex_python.converter import CurrencyRates

currency_rates = CurrencyRates()

def convert_currency(amount, from_currency, to_currency):
    try:
        rate = currency_rates.get_rate(from_currency, to_currency)
        return round(amount * rate, 2)
    except Exception as e:
        print(f"Currency Conversion Error: {e}")
        return None
