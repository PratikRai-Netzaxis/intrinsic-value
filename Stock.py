import requests
from bs4 import BeautifulSoup
import stock_info as si
from yahoofinancials import YahooFinancials as YF
import json
import re
import math


class Stock:
    GROWTH_DECLINE_RATE = 0.05
    VALUATION_LAST_FCF = 12
    MARGIN_OF_SAFETY = 0.30

    def __init__(self, ticker, name, risk_free_return):
        yf_stock = YF(ticker)
        yf_stats = si.get_stats(ticker)
        key_statistics = yf_stock.get_key_statistics_data()

        self.ticker = ticker

        self.name = name

        self.risk_free_return = risk_free_return

        self.beta = self.get_beta(yf_stock, yf_stats)

        self.wacc = self.get_wacc(yf_stock)

        self.growth_estimate_per_annum = self.get_growth_estimate_per_annum()

        self.conservative_growth_rate = self.get_conservative_growth_rate()

        self.recommendation_rating = self.get_recommendation_rating()

        self.free_cash_flow = self.get_free_cash_flow()

        self.price = round(si.get_live_price(ticker), 2)

        self.shares_outstanding = float(
            round(key_statistics[self.ticker]['sharesOutstanding'] / 1000000, 2))

        self.profit_margin = yf_stats["Value"][30]

        self.operating_margin = yf_stats["Value"][31]

        self.return_on_assets = yf_stats["Value"][32]

        self.return_on_equity = yf_stats["Value"][33]

        self.book_value = yf_stats["Value"][56]

        self.quarterly_revenue_growth_yoy = yf_stats["Value"][36]

        self.cash = yf_stats["Value"][51]

        self.trailing_pe = self.get_trailing_pe(yf_stock)

        self.price_per_book = round(self.price / float(self.book_value), 2)

        self.cash_and_cash_equivalents = float(
            re.sub("[^\d\.\-]", "", self.cash)) * 1000

        self.total_liabilities = self.get_total_liabilities(yf_stock)

        self.intrinsic_value = self.get_intrinsic_value()

        self.potential_upside = self.get_potential_upside()

        self.trailing_pe_pb_multiple = round(
            self.trailing_pe * self.price_per_book, 2)

    def get_beta(self, yf_stock, yf_stats):
        yf_stats_beta = yf_stats["Value"][0]
        yf_stock_beta = yf_stock.get_beta()
        if (type(yf_stats_beta) == int or type(yf_stats_beta) == float and not math.isnan(yf_stats_beta)):
            return yf_stats_beta
        elif (type(yf_stock_beta) == int or type(yf_stock_beta) == float and not math.isnan(yf_stock_beta)):
            return yf_stock_beta
        else:
            return 1

    def get_first_quarter_key(self, yf_stock):
        balance_sheet_data_qt = yf_stock.get_financial_stmts(
            frequency='quarterly', statement_type='balance')
        var = list(
            balance_sheet_data_qt["balanceSheetHistoryQuarterly"][self.ticker])
        first_quarter = var.pop(0)
        key = list(first_quarter)[0]
        return first_quarter, key

    def get_total_liabilities(self, yf_stock):
        balance_sheet = yf_stock.get_financial_stmts('quarterly', 'balance')
        balance_sheet_last_quarter = list(
            balance_sheet['balanceSheetHistoryQuarterly'][self.ticker][0].values())[0]
        totalLiab = balance_sheet_last_quarter['totalLiab']

        return float(totalLiab) / 1000000

    def get_trailing_pe(self, yf_stock):
        if yf_stock.get_pe_ratio() is not None:
            return round(yf_stock.get_pe_ratio(), 2)
        else:
            return -1

    def get_free_cash_flow(self):
        free_cash_flow = float(si.get_cash_flow_trailing(
            self.ticker.replace(".", "-"))) / 1000000
        return free_cash_flow

    def get_growth_estimate_per_annum(self):
        url_analyst_predictions = f'https://finance.yahoo.com/quote/{self.ticker}/analysis?ltr=1'
        r_analyst_predictions = requests.get(url_analyst_predictions)
        r_analyst_predictions_html = r_analyst_predictions.text
        data = json.loads(re.search('root\.App\.main\s*=\s*(.*);',
                                    r_analyst_predictions_html).group(1))
        field = [t for t in data["context"]["dispatcher"]["stores"]["QuoteSummaryStore"]["earningsTrend"]["trend"] if
                 t["period"] == "+5y"][0]
        growth_estimate_per_annum = float(
            field["growth"]["fmt"].replace('%', ''))
        return growth_estimate_per_annum

    def get_recommendation_rating(self):
        url = f'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{self.ticker}?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&modules=upgradeDowngradeHistory,recommendationTrend,financialData,earningsHistory,earningsTrend,industryTrend&corsDomain=finance.yahoo.com'
        r = requests.get(url)
        if not r.ok:
            recommendation = 6
        try:
            result = r.json()['quoteSummary']['result'][0]
            recommendation = result['financialData']['recommendationMean']['fmt']
        except:
            recommendation = 6
        return recommendation

    def get_conservative_growth_rate(self):
        if self.growth_estimate_per_annum > 0:
            conservative_growth_rate = (
                self.growth_estimate_per_annum * (1 - self.MARGIN_OF_SAFETY) / 100)
        else:
            conservative_growth_rate = (
                self.growth_estimate_per_annum * (1 + self.MARGIN_OF_SAFETY) / 100)
        return conservative_growth_rate

    def get_cost_of_equity(self, yf_stock):
        market_risk_premium = 7.5
        return round(self.risk_free_return + (self.beta * market_risk_premium), 2)

    def get_last_annual_balance_sheet(self, yf_stock):
        balance_sheet = list(yf_stock.get_financial_stmts('annual', 'balance')[
            "balanceSheetHistory"][self.ticker][0].values())[0]
        return balance_sheet

    def get_last_quarter_balance_sheet(self, yf_stock):
        balance_sheet = list(yf_stock.get_financial_stmts('quarterly', 'balance')[
            "balanceSheetHistoryQuarterly"][self.ticker][0].values())[0]
        return balance_sheet

    def get_last_annual_income_stmt(self, yf_stock):
        income_stmt = list(yf_stock.get_financial_stmts('annual', 'income')[
            "incomeStatementHistory"][self.ticker][0].values())[0]
        return income_stmt

    def get_weighted_avg_cost_of_equity(self, yf_stock):
        last_quarter_balance_sheet = self.get_last_quarter_balance_sheet(
            yf_stock)

        cost_of_equity = self.get_cost_of_equity(yf_stock)

        current_total_debt = (last_quarter_balance_sheet["shortLongTermDebt"] if "shortLongTermDebt" in last_quarter_balance_sheet else 0) + (
            last_quarter_balance_sheet["longTermDebt"] if "longTermDebt" in last_quarter_balance_sheet else 0)

        current_total_equity = last_quarter_balance_sheet["totalStockholderEquity"]

        sum_total_equity_total_debt = current_total_equity + current_total_debt

        weighted_avg_cost_of_equity = (
            current_total_equity/sum_total_equity_total_debt) * cost_of_equity

        return weighted_avg_cost_of_equity

    def get_weighted_avg_cost_of_debt(self, yf_stock):
        last_quarter_balance_sheet = self.get_last_quarter_balance_sheet(
            yf_stock)
        last_annual_income_stmt = self.get_last_annual_income_stmt(yf_stock)
        last_annual_balance_sheet = self.get_last_annual_balance_sheet(
            yf_stock)

        current_total_debt = (last_quarter_balance_sheet["shortLongTermDebt"] if "shortLongTermDebt" in last_quarter_balance_sheet else 0) + (
            last_quarter_balance_sheet["longTermDebt"] if "longTermDebt" in last_quarter_balance_sheet else 0)

        last_annual_total_debt = (last_annual_balance_sheet["shortLongTermDebt"] if "shortLongTermDebt" in last_annual_balance_sheet else 0) + (
            last_annual_balance_sheet["longTermDebt"] if "longTermDebt" in last_annual_balance_sheet else 0)

        current_total_equity = last_quarter_balance_sheet["totalStockholderEquity"]

        sum_current_total_equity_total_debt = current_total_equity + current_total_debt

        cost_of_debt = last_annual_income_stmt["incomeTaxExpense"] / (
            last_annual_total_debt or 1)

        tax_rate = yf_stock.get_income_tax_expense() / yf_stock.get_income_before_tax()

        weighted_avg_cost_of_debt = (
            current_total_debt/sum_current_total_equity_total_debt) * cost_of_debt * (1 - tax_rate)

        return weighted_avg_cost_of_debt

    def get_wacc(self, yf_stock):
        weighted_avg_cost_of_equity = self.get_weighted_avg_cost_of_equity(
            yf_stock)

        weighted_avg_cost_of_debt = self.get_weighted_avg_cost_of_debt(
            yf_stock)

        wacc = round((weighted_avg_cost_of_equity +
                      weighted_avg_cost_of_debt) / 100, 2)

        return wacc

    def get_company_value(self):
        a = [[None, None] for i in range(11)]
        total_npv_fcf = 0.0

        for year in range(1, 11):
            if year == 1:
                fcf_growth_rate = round(
                    self.free_cash_flow * (1 + self.conservative_growth_rate), 2)
                npv_fcf = round(fcf_growth_rate /
                                (1 + self.wacc) ** year, 2)
                a[year][0] = fcf_growth_rate
                a[year][1] = npv_fcf
                total_npv_fcf += npv_fcf
            else:
                fcf_growth_rate = round(
                    a[year - 1][0] * (1 + self.conservative_growth_rate * ((1 - self.GROWTH_DECLINE_RATE) ** (year - 1))), 2)
                npv_fcf = round(fcf_growth_rate /
                                (1 + self.wacc) ** year, 2)
                a[year][0] = fcf_growth_rate
                a[year][1] = npv_fcf
                total_npv_fcf += npv_fcf

        year_ten_fcf_value = a[10][1] * self.VALUATION_LAST_FCF
        company_value = round(total_npv_fcf + year_ten_fcf_value +
                              self.cash_and_cash_equivalents - self.total_liabilities, 2)
        return company_value

    def get_intrinsic_value(self):
        intrinsic_value = round(
            self.get_company_value() / self.shares_outstanding, 2)
        return intrinsic_value

    def get_potential_upside(self):
        potential_upside = round(
            ((self.get_intrinsic_value() - self.price) / self.price) * 100, 2)
        return potential_upside
