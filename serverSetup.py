import sqlalchemy
import pymysql
import pandas as pd
import yfinance as yf

pymysql.install_as_MySQLdb()

indices = ['DJGT50']

def schemaCreate(index):
    engine = sqlalchemy.create_engine('mysql://root:dspA123@localhost:3306/')
    engine.execute(sqlalchemy.schema.CreateSchema(index))

for index in indices:
    schemaCreate(index)

djgt50 = pd.read_excel('ticker.xlsx', engine='openpyxl')
djgt50 = djgt50.Ticker.to_list()
print(djgt50)
mapper = {'DJGT50':djgt50}

for index in indices:
    engine = sqlalchemy.create_engine('mysql://root:dspA123@localhost:3306/'+index)
    for symbol in mapper[index]:
        df = yf.download(symbol, start='2020-01-01')
        df = df.reset_index()
        df.to_sql(symbol, engine)