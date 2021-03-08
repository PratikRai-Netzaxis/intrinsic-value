from Stock import Stock
from utilities.downloaders.us_yield import get_10y_us_bond_yield


def print_stock_valuation(stock):
    message = f"""
    {stock.ticker}
    Stock price: {stock.price}
    Intrinsic value: {stock.intrinsic_value}
    Potential upside: {stock.potential_upside}
    Average recommendation: {stock.recommendation_rating}
    """
    print(message)


def run_single_company_valuation():
    ticker = 'AAPL'
    company_name = 'Apple inc.'
    risk_free_return = get_10y_us_bond_yield()

    stock = Stock(ticker, company_name, risk_free_return)

    print_stock_valuation(stock)


run_single_company_valuation()
