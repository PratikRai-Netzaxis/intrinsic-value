from Stock import Stock
from us_yield import get_10y_us_bond_yield

ticker = 'AAPL'
company_name = 'Apple'
risk_free_return = get_10y_us_bond_yield()

stock_details = Stock(ticker, company_name, risk_free_return)