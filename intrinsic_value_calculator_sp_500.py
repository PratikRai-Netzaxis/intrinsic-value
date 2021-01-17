from run_valuation_from_file import run_valuation_for
from us_yield import get_10y_us_bond_yield

if __name__ == '__main__':
    INDEX_NAME = 'SP500'
    SP500_COMPANIES = './data/SP500stocks.csv'
    TEN_Y_US_BOND_YIELD = float(get_10y_us_bond_yield())

    run_valuation_for(SP500_COMPANIES, INDEX_NAME, TEN_Y_US_BOND_YIELD)
