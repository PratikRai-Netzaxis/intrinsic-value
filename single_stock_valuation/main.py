from Stock import Stock
from utilities.downloaders.us_yield import get_10y_us_bond_yield


def get_stock_valuation_str_formated(stock):
    message = f"""
    {stock.ticker}
    Stock price: {stock.price}
    Intrinsic value: {stock.intrinsic_value}
    Potential upside: {stock.potential_upside}
    Average recommendation: {stock.recommendation_rating}
    """
    return message


def run_single_company_valuation(request):
    ticker = 'AAPL'
    company_name = 'Apple inc.'
    risk_free_return = get_10y_us_bond_yield()

    stock = Stock(ticker, company_name, risk_free_return)

    return get_stock_valuation_str_formated(stock)
