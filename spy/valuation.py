from run_valuation_from_file import run_valuation_for
from utilities.downloaders.us_yield import get_10y_us_bond_yield

if __name__ == '__main__':
    INDEX_NAME = 'SP500'
    SP500_COMPANIES = './spy_companies.csv'
    TEN_Y_US_BOND_YIELD = get_10y_us_bond_yield()

    run_valuation_for(SP500_COMPANIES, INDEX_NAME, TEN_Y_US_BOND_YIELD)
