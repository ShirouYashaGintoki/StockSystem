import yfinance as yf
from datetime import datetime, timedelta

days = datetime.timedelta(1)
start = datetime.today().strftime('%Y-%m-%d') - days
end = datetime.today().strftime('%Y-%m-%d')
tsla = yf.ticker('tsla')
tslahist = tsla.history(period='1mo', interval='5min', start=start, end=end, auto_adjust=False, rounding=True)

# percent_diff = (((float(second_number) - float(first_number))/float(first_number)) * 100)
# prefix = "+" if percent_diff > 0 else ''
# print(f'Difference is {prefix}{percent_diff:.2f}%')

# Use alpha x2 to do mover updates every 30 mins/hour