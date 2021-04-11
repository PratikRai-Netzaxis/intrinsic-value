from run_valuation_from_file import run_valuation_for
from utilities.downloaders.us_yield import get_10y_us_bond_yield
import os
from google.cloud import bigquery
import logging
import traceback


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


@try_catch_log
def run_nasdaq_valuation(request):
    INDEX_NAME = 'Nasdaq'
    NASDAQ_COMPANIES = './nasdaq_companies.csv'
    TEN_Y_US_BOND_YIELD = get_10y_us_bond_yield()

    rows = run_valuation_for(NASDAQ_COMPANIES, INDEX_NAME, TEN_Y_US_BOND_YIELD)

    load_data_to_bigquery(rows)
