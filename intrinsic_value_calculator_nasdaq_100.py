from run_valuation_from_file import run_valuation_for
from us_yield import get_10y_us_bond_yield

if __name__ == '__main__':
    INDEX_NAME = 'Nasdaq'
    NASDAQ_COMPANIES = './data/Nasdaq_100.csv'
    TEN_Y_US_BOND_YIELD = get_10y_us_bond_yield()

    run_valuation_for(NASDAQ_COMPANIES, INDEX_NAME, TEN_Y_US_BOND_YIELD)