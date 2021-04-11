from csv import reader
import datetime
from Stock import Stock

date = str(datetime.now().date())


def run_valuation_for(companies, index_name, ten_year_us_bond_yield):

    def create_stock_details_row(stock):
        return {
            "name": stock.name,
            "ticker": stock.ticker,
            "current_value": stock.price,
            "intrinsic_value": stock.intrinsic_value,
            "date": date, "sector": "", "index": index_name,
            "intrinsic_value_category": stock.intrinsic_value_category
        }

    valuation = []

    with open(companies, 'r') as read_obj:
        csv_reader = reader(read_obj)
        next(csv_reader)
        for reader_row in csv_reader:
            ticker = reader_row.__getitem__(0).replace(".", "-")
            company_name = reader_row.__getitem__(1)

            stock = Stock(ticker, company_name, ten_year_us_bond_yield)

            stock_details_row = create_stock_details_row(stock)

            valuation.append(stock_details_row)

    return valuation
