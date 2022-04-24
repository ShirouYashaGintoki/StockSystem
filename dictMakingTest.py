import pandas as pd

df = pd.read_excel('tickers2.xlsx', sheet_name='Sheet 2')

newDict = pd.Series(df.Symbol.values, index=df.CompanyName).to_dict()

print(newDict)