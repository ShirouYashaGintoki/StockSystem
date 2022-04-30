import mysql.connector
import pymysql
from sqlalchemy import create_engine
import sqlalchemy


# beansontoastA1? for PC
# dspA123 for laptop
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="dspA123",
    database="testdb"
)

# pymysql.install_as_MySQLdb()

# def schemaMaker(schemaName):
#     # my_conn = create_engine("mysql+mysqldb://root:beansontoastA1?@localhost/testdb")
#     engine = sqlalchemy.create_engine('mysql://root:beansontoastA1?@localhost:3306/')
#     engine.execute(sqlalchemy.schema.CreateSchema(schemaName))



my_cursor = db.cursor()
# my_cursor.execute("CREATE DATABASE testdb")
testName = "beans"
testList = ["5", "30", "60"]
# schemaMaker(test)

# engine = sqlalchemy.create_engine('mysql://root:beansontoastA1?@localhost:3306/'+test)
for timeFrame in testList:
    try:
        print(timeFrame)
        my_cursor.execute("""CREATE TABLE IF NOT EXISTS %s (
        date_time DATETIME,
        close FLOAT(5),
        ema12 FLOAT(2),
        ema26 FLOAT(2),
        macd FLOAT(7),
        buysellsignal FLOAT(6))
        """ %(timeFrame))
    except Exception as e:
        print(f'Error: {e}')
    

# my_cursor.execute("DESCRIBE beans")

# for x in my_cursor:
#     print(x)


# db.close()

