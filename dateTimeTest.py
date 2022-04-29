import pandas as pd

indices = pd.read_excel('tickers2.xlsx', sheet_name='Sheet 1')
# Create a dictionary of stock names and their ticker symbols
indDict = pd.Series(indices.Symbol.values, index=indices.CompanyName).to_dict()
# Create a list of stock names for display purposes
stockNameList = sorted(list(indDict.keys()))

key = "APPLE INC."

print(indDict[key])