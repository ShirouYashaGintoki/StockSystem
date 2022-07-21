from configparser import ConfigParser

def ftConfigSetup():
    # Get the configparser object
    config_object = ConfigParser()

    # Store API, DATABASE and Stock settings
    config_object["API"] = {
        "url" : "https://twelve-data1.p.rapidapi.com/time_series",
        "apiheader" : "twelve-data1.p.rapidapi.com",
        "apikey" : "d9d76c3270msh16a19417bd4b485p1b0395jsn955227be6f56"
    }

    config_object["DATABASE"] = {
        "host": "localhost",
        "user": "root",
        "password": "beansontoastA1?",
        "dbname": "StockTables",
        "dblink" : "mysql://root:beansontoastA1?@localhost:3306/stocktables"
    }

    config_object["STOCKCONFIG"] = {
        "stock1": "APPLE",
        "time1": "5MIN",

        "stock2": "MICROSOFT",
        "time2": "5MIN",

        "stock3": "ALPHABET",
        "time3": "5MIN",

        "stock4": "AMAZON.COM",
        "time4": "5MIN",

        "stock5": "TESLA",
        "time5": "5MIN"
    }

    # Write the above sections to config.ini file
    with open('config.ini', 'w') as conf:
        config_object.write(conf)