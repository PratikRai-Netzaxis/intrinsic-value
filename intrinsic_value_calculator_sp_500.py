from run_valuation_from_file import run_valuation_for

if __name__ == '__main__':
    INDEX_NAME = 'SP500'
    SP500_COMPANIES = './data/SP500stocks.csv'
    run_valuation_for(SP500_COMPANIES, INDEX_NAME)
