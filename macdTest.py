import yfinance as yf
import matplotlib.pyplot as plt

df = yf.download('AMZN', start='2022-01-19')

df['EMA12'] = df.Close.ewm(span=12).mean()
df['EMA26'] = df.Close.ewm(span=26).mean()
df['MACD'] = df.EMA12 - df.EMA26
df['signal'] = df.MACD.ewm(span=9).mean()
print('indicators added')

# plt.plot(df.signal, label='Signal Line', color='red')
# plt.plot(df.MACD, label='MACD', color='green')
# plt.legend()
# plt.show()

print("before \n-------------")
print(df)

Buy, Sell = [], []

for i in range(2, len(df)):
    if df.MACD.iloc[i] > df.signal.iloc[i] and df.MACD.iloc[i-1] < df.signal.iloc[i-1]:
        Buy.append(i)
    elif df.MACD.iloc[i] < df.signal.iloc[i] and df.MACD.iloc[i-1] > df.signal.iloc[i-1]:
        Sell.append(i)

 
idk = df.iloc[Buy].index

df = df.iloc[::-1]

print("after \n-------------")
print(df)
print(df.iloc[0])
# print(idk)

# for dateTime in idk:
#     print("Buy", dateTime, end="\n")

# poo = df.iloc[Sell].index
# for dateTime in poo:
#     print("Sell", dateTime, end="\n")