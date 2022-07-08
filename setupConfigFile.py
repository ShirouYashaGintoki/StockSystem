from configparser import ConfigParser

def ftConfigSetup():
    #Get the configparser object
    config_object = ConfigParser()

    #Assume we need 2 sections in the config file, let's call them USERINFO and SERVERCONFIG
    config_object["DATABASE"] = {
        "host": "localhost",
        "user": "root",
        "password": "beansontoastA1?",
        "dbname": "StockTables"
    }

    config_object["STOCKCONFIG"] = {
        "stock1": "ABT",
        "time1": "5min",

        "stock2": "ABBV",
        "time2": "5min",

        "stock3": "ACN",
        "time3": "5min",

        "stock4": "ADBE",
        "time4": "5min",

        "stock5": "AMD",
        "time5": "5min"
    }

    #Write the above sections to config.ini file
    with open('config.ini', 'w') as conf:
        config_object.write(conf)