import pandas as pd
  
arr = [287.72, 287.93, 290.73, 299.50, 300.47, 295.00]
window_size = 3
  
# Convert array of integers to pandas series
numbers_series = pd.Series(arr)
  
# Get the window of series
# of observations of specified window size
windows = numbers_series.rolling(window_size)
  
# Create a series of moving
# averages of each window
moving_averages = windows.mean()
  
# Convert pandas series back to list
moving_averages_list = moving_averages.tolist()
  
# Remove null entries from the list
final_list = moving_averages_list[window_size - 1:]

for entry in final_list:
    entry2 = round(entry, 3)
    final_list[final_list.index(entry)] = entry2

print(final_list)

