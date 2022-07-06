import pandas as pd
import mplfinance as mpf
import numpy as np

list1 = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 184.37, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 183.43, np.nan, 183.64, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]

list2 = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 183.59, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 183.3, np.nan, np.nan, np.nan, np.nan, 183.39, np.nan, np.nan]

if any(isinstance(j,float) for j in list1):
    print("int found!")
else:
    print("no int found")