from run_valuation_from_file import run_valuation_for
from utilities.downloaders.us_yield import get_10y_us_bond_yield


def run_nasdaq_valuation(request):
    INDEX_NAME = 'Nasdaq'
    NASDAQ_COMPANIES = './nasdaq_companies.csv'
    TEN_Y_US_BOND_YIELD = get_10y_us_bond_yield()

    run_valuation_for(NASDAQ_COMPANIES, INDEX_NAME, TEN_Y_US_BOND_YIELD)
