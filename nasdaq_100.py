import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://en.wikipedia.org/wiki/NASDAQ-100"
r = requests.get(url)
r_html = r.text
soup = BeautifulSoup(r_html, 'html.parser')
print(soup.text)
components_table = soup.find_all(id="constituents")
print(components_table)
headers_html = soup.find_all("th")
df_columns = [item.text.rstrip("\n") for item in headers_html]
components_headers = df_columns[:4]
data_rows = components_table[0].find("tbody").find_all("tr")[1:]
rows = []
for row in range(len(data_rows)):
    stock = list(filter(None, data_rows[row].text.split("\n")))
    rows.append(stock)
Nasdaq_100_stocks = pd.DataFrame(rows, columns=components_headers)
Nasdaq_100_stocks.to_csv(r"/users/akarapetsas/Desktop/value_investing/Nasdaq_100.csv", index=False, encoding='utf-8')
