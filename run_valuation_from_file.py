import pandas
from csv import reader
import datetime
import sys
import os
from Stock import Stock


def run_valuation_for(companies, output_dir_name):
    CURRENT_DATE = datetime.datetime.today().strftime('%d-%b-%Y')
    ANALYSIS_COLUMNS = ['TICKER',
                        ' SECURITY ',
                        ' INTRINSIC VALUE ',
                        ' STOCK PRICE ',
                        ' POTENTIAL UPSIDE ',
                        ' P/E trailing ',
                        ' P/B ',
                        ' P/E * P/B ',
                        ' Profit Margin ',
                        ' Operating Margin ',
                        ' Return on Assets ',
                        ' Return on Equity ',
                        ' Quarterly Revenue Growth (YoY) ',
                        ' Recommendation Rating ']

    def create_stock_details_row(stock):
        return [
            stock.ticker,
            stock.name,
            str(stock.intrinsic_value),
            str(stock.price),
            (str(stock.potential_upside) + "%"),
            stock.trailing_pe,
            stock.price_per_book,
            str(stock.trailing_pe_pb_multiple),
            stock.profit_margin,
            stock.operating_margin,
            stock.return_on_assets,
            stock.return_on_equity,
            stock.quarterly_revenue_growth_yoy,
            stock.conservative_growth_rate]

    def print_stock_valuation(stock):
        message = f"""
        {'='*30}
        {stock.ticker}
        Stock price: {stock.price}
        Intrinsic value: {stock.intrinsic_value}
        Potential upside: {stock.potential_upside}
        Average recommendation: {stock.recommendation_rating}
        """
        print(message)

    def save_valuation_to_csv(rows, filename):
        S_P_500_stocks_dfc = pandas.DataFrame(rows, columns=ANALYSIS_COLUMNS)

        S_P_500_stocks_dfc.to_csv(
            f'./recommendations/{output_dir_name}/{CURRENT_DATE}/{filename}.csv', index=False,
            encoding='utf-8')

    all_company_valuation = []
    fair_value_companies = []
    better_value_companies = []

    with open(companies, 'r') as read_obj:
        csv_reader = reader(read_obj)
        next(csv_reader)
        for reader_row in csv_reader:
            try:
                ticker = reader_row.__getitem__(0).replace(".", "-")
                company_name = reader_row.__getitem__(1)

                stock = Stock(ticker, company_name)

                print_stock_valuation(stock)

                stock_details_row = create_stock_details_row(stock)

                all_company_valuation.append(stock_details_row)

                if stock.potential_upside > 0.0 and stock.trailing_pe_pb_multiple <= 25 and stock.conservative_growth_rate <= 3.00:
                    better_value_companies.append(stock_details_row)

                if stock.potential_upside > 0.0 or stock.trailing_pe_pb_multiple <= 25:
                    fair_value_companies.append(stock_details_row)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print("Exception on valuation")

    save_valuation_to_csv(all_company_valuation, 'all_company_valuation')
    save_valuation_to_csv(fair_value_companies, 'fair_value_companies')
    save_valuation_to_csv(better_value_companies, 'better_value_companies')
