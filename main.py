# from run_valuation_from_file import run_valuation_for
from utilities.downloaders.us_yield import get_10y_us_bond_yield
import os
from google.cloud import bigquery
import logging
import traceback
from Stock import Stock
import datetime


date = str(datetime.now().date())


def try_catch_log(wrapped_func):
    def wrapper(*args, **kwargs):
        try:
            response = wrapped_func(*args, **kwargs)
        except Exception:
            # Replace new lines with spaces so as to prevent several entries which
            # would trigger several errors.
            error_message = traceback.format_exc().replace('\n', '  ')
            logging.error(error_message)
            return 'Error'
        return response
    return wrapper


def load_data_to_bigquery(rows):
    client = bigquery.Client()

    dataset_ref = client.dataset(os.environ['DATASET'])
    table_id = dataset_ref.table(os.environ['TABLE'])

    errors = client.insert_rows_json(table_id, rows)
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))


def create_stock_details_row(stock):
    return {
        "name": stock.name,
        "ticker": stock.ticker,
        "current_value": stock.price,
        "intrinsic_value": stock.intrinsic_value,
        "date": date, "sector": "", "index": 'Nasdaq',
        "intrinsic_value_category": stock.intrinsic_value_category
    }


@try_catch_log
def run_nasdaq_valuation(request):
    # INDEX_NAME = 'Nasdaq'
    # NASDAQ_COMPANIES = './nasdaq_companies.csv'
    TEN_Y_US_BOND_YIELD = get_10y_us_bond_yield()

    rows = []

    stock = Stock('AAPL', 'Apple inc.', TEN_Y_US_BOND_YIELD)

    row = create_stock_details_row(stock)

    rows.append(row)

    load_data_to_bigquery(rows)
