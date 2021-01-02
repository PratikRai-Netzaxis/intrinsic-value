import requests
from bs4 import BeautifulSoup
import pandas as pd
from yahoo_fin import stock_info as si
from yahoofinancials import YahooFinancials
import numpy as np
import pandas
from csv import reader
import datetime

current_date = datetime.datetime.today().strftime('%d-%b-%Y')


def get_recommendation_rating(ticker):
    lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
    rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
              'modules=upgradeDowngradeHistory,recommendationTrend,' \
              'financialData,earningsHistory,earningsTrend,industryTrend&' \
              'corsDomain=finance.yahoo.com'

    url = lhs_url + ticker + rhs_url
    r = requests.get(url)
    if not r.ok:
        recommendation = 6
    try:
        result = r.json()['quoteSummary']['result'][0]
        recommendation = result['financialData']['recommendationMean']['fmt']
    except:
        recommendation = 6

    print("{} has an average recommendation of: ".format(ticker), recommendation)
    return recommendation


def get_first_key(first_quarter):
    for key in first_quarter:
        return key


def ticker_intrinsic_value_calculator(stock_details):
    row = []
    stock_ticker = stock_details.__getitem__(1)
    print("--------------------------------------------")
    print("Ticker " + stock_ticker)

    url_analyst_predictions = "https://finance.yahoo.com/quote/%s/analysis?ltr=1"
    r_analyst_predictions = requests.get(url_analyst_predictions % (stock_ticker.replace(".", "-")))
    r_analyst_predictions_html = r_analyst_predictions.text
    soup_analyst_predictions = BeautifulSoup(r_analyst_predictions_html, 'html.parser')

    growth_estimate_per_annum = 0.0
    if soup_analyst_predictions.find('td', attrs={'data-reactid': '427'}):
        growth_estimate_per_annum = float(
            soup_analyst_predictions.find('td', attrs={'data-reactid': '427'}).contents[0].replace('%', ''))

    cash_flow_data = si.get_cash_flow(stock_ticker.replace(".", "-"), yearly=False)
    free_cash_flow = (pandas.DataFrame(cash_flow_data, index=['totalCashFromOperatingActivities']).sum(axis=1)[
                          'totalCashFromOperatingActivities'] +
                      pandas.DataFrame(cash_flow_data, index=['capitalExpenditures']).sum(axis=1)[
                          'capitalExpenditures']) // 1000000

    # free_cash_flow = float(si.get_cash_flow_trailing(stock_ticker.replace(".", "-"))) / 1000000

    stock_price = round(si.get_live_price(stock_ticker.replace(".", "-")), 2)

    stats = si.get_stats(stock_ticker.replace(".", "-"))
    shares = str(stats["Value"][9])
    if "B" in shares:
        shares_outstanding = float(shares.replace('B', '')) * 1000
    else:
        shares_outstanding = float(shares.replace('M', ''))

    profit_margin = stats["Value"][30]
    operating_margin = stats["Value"][31]
    return_on_assets = stats["Value"][32]
    return_on_equity = stats["Value"][33]
    quarterly_revenue_growth_yoy = stats["Value"][36]

    yahoo_financial = YahooFinancials(stock_ticker)

    price_per_earnings_trailing = -1
    if yahoo_financial.get_pe_ratio() is not None:
        price_per_earnings_trailing = round(yahoo_financial.get_pe_ratio(), 2)

    price_per_book = round(yahoo_financial.get_current_price() / (
            yahoo_financial.get_book_value() / yahoo_financial.get_num_shares_outstanding()), 2)

    balance_sheet_data_qt = yahoo_financial.get_financial_stmts(frequency='quarterly', statement_type='balance')
    var = list(balance_sheet_data_qt["balanceSheetHistoryQuarterly"][stock_ticker])
    first_quarter = var.pop(0)
    key = get_first_key(first_quarter)
    cash_and_cash_equivalents_string = first_quarter[key]["cash"]
    cash_and_cash_equivalents = float(cash_and_cash_equivalents_string) / 1000000

    total_liabilities_string = first_quarter[key]["totalLiab"]
    total_liabilities = float(total_liabilities_string) / 1000000

    growth_decline_rate = 0.05
    discount_rate = 0.09
    valuation_last_fcf = 12
    margin_of_safety = 0.30
    if growth_estimate_per_annum > 0:
        conservative_growth_rate = (growth_estimate_per_annum * (1 - margin_of_safety) / 100)
    else:
        conservative_growth_rate = (growth_estimate_per_annum * (1 + margin_of_safety) / 100)

    a = [[None] * 2] * 11
    total_npv_fcf = 0.0

    for year in range(1, 11):
        if year == 1:
            fcf_growth_rate = round(free_cash_flow * (1 + conservative_growth_rate), 2)
            npv_fcf = round(fcf_growth_rate / (1 + discount_rate) ** year, 2)
            a[year][0] = fcf_growth_rate
            a[year][1] = npv_fcf
            total_npv_fcf += npv_fcf
        else:
            fcf_growth_rate = round(
                a[year - 1][0] * (1 + conservative_growth_rate * ((1 - growth_decline_rate) ** (year - 1))), 2)
            npv_fcf = round(fcf_growth_rate / (1 + discount_rate) ** year, 2)
            a[year][0] = fcf_growth_rate
            a[year][1] = npv_fcf
            total_npv_fcf += npv_fcf

    year_ten_fcf_value = a[10][1] * valuation_last_fcf
    company_value = round(total_npv_fcf + year_ten_fcf_value + cash_and_cash_equivalents - total_liabilities, 2)
    intrinsic_value = round(company_value / shares_outstanding, 2)
    print("Intrinsic value " + str(intrinsic_value))
    print("Stock price: " + str(stock_price))

    potential_upside = round(((intrinsic_value - stock_price) / stock_price) * 100, 2)
    print("Potential upside " + str(potential_upside) + "%")

    row.append(stock_ticker)
    row.append(stock_details.__getitem__(0))
    row.append(str(intrinsic_value))
    row.append(str(stock_price))
    row.append(str(potential_upside) + "%")
    row.append(price_per_earnings_trailing)
    row.append(price_per_book)
    row.append(str(round(float(price_per_earnings_trailing) * float(price_per_book), 2)))
    row.append(profit_margin)
    row.append(operating_margin)
    row.append(return_on_assets)
    row.append(return_on_equity)
    row.append(quarterly_revenue_growth_yoy)
    row.append(get_recommendation_rating(stock_ticker))
    return row


dfc_rows_nasdaq_100 = []

with open('/users/akarapetsas/Desktop/value_investing/Nasdaq_100.csv', 'r') as read_obj:
    csv_reader = reader(read_obj)
    for reader_row in csv_reader:
        try:
            dfc_rows_nasdaq_100.append(ticker_intrinsic_value_calculator(reader_row))
        except:
            print("Exception on dfc_rows")

Nasdaq_100_stocks_dfc = pandas.DataFrame(dfc_rows_nasdaq_100, columns=['TICKER',
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
                                                                       ' Recommendation Rating '])

Nasdaq_100_stocks_dfc.to_csv(
    fr"/users/akarapetsas/Desktop/value_investing/IntrinsicValues_Nasdaq_100_{current_date}.csv", index=False,
    encoding='utf-8')

pe_pb_valuation_row = []
for dfc_row in dfc_rows_nasdaq_100:
    try:
        if float(dfc_row.__getitem__(4).replace("%", "")) > 0.0 or float(dfc_row.__getitem__(7)) <= 25:
            pe_pb_valuation_row.append(dfc_row)
    except:
        print("Exception on pe_pb_valuation_row")

Nasdaq_100_stocks_simple_valuation = pandas.DataFrame(pe_pb_valuation_row, columns=['TICKER',
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
                                                                                    ' Recommendation Rating '])

Nasdaq_100_stocks_simple_valuation.to_csv(
    fr"/users/akarapetsas/Desktop/value_investing/IntrinsicValues_Nasdaq_100_Low_Valued_{current_date}.csv",
    index=False, encoding='utf-8')

final_valuation_rows = []
for dfc_row in dfc_rows_nasdaq_100:
    try:
        if float(dfc_row.__getitem__(4).replace("%", "")) > 0.0 and float(dfc_row.__getitem__(7)) <= 25 and float(
                dfc_row.__getitem__(13)) <= 2.50:
            final_valuation_rows.append(dfc_row)
    except:
        print("Exception on pe_pb_valuation_row")

Nasdaq_100_stocks_simple_valuation = pandas.DataFrame(final_valuation_rows, columns=['TICKER',
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
                                                                                     ' Recommendation Rating '])

Nasdaq_100_stocks_simple_valuation.to_csv(
    fr"/users/akarapetsas/Desktop/value_investing/IntrinsicValues_Nasdaq_100_Low_Valued_Final_{current_date}.csv",
    index=False, encoding='utf-8')
