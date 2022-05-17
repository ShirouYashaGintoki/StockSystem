import pandas as pd

df1=pd.DataFrame({'A':[1,2,3,3],'B':[2,3,4,4]})
df2=pd.DataFrame({'A':[1],'B':[2]})

# df1 = df1.drop_duplicates(keep='last')
print(df1)
print("\n")
# df2 = df2.drop_duplicates(keep='last')
print(df2)
print("\n")

# df3 = df1[~df1.apply(tuple,1).isin(df2.apply(tuple,1))]
# df3 = df1.merge(df2,indicator = True, how='left').loc[lambda x : x['_merge']!='both']
print(df3)