import yfinance as yf
import matplotlib.pyplot as plt

df = yf.download('AMZN', start='2021-01-06')

df['EMA12'] = df.Close.ewm(span=12).mean()
df['EMA26'] = df.Close.ewm(span=26).mean()
df['MACD'] = df.EMA12 - df.EMA26
df['signal'] = df.MACD.ewm(span=9).mean()
print('indicators added')

# plt.plot(df.signal, label='Signal Line', color='red')
# plt.plot(df.MACD, label='MACD', color='green')
# plt.legend()
# plt.show()

# print(df)

Buy, Sell = [], []

for i in range(2, len(df)):
    if df.MACD.iloc[i] > df.signal.iloc[i] and df.MACD.iloc[i-1] < df.signal.iloc[i-1]:
        Buy.append(i)
    elif df.MACD.iloc[i] < df.signal.iloc[i] and df.MACD.iloc[i-1] > df.signal.iloc[i-1]:
        Sell.append(i)

 
idk = df.iloc[Buy].index

# for dateTime in idk:
#     print(dateTime, end="\n")