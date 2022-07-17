from configparser import ConfigParser

def ftConfigSetup():
    #Get the configparser object
    config_object = ConfigParser()

    #Assume we need 2 sections in the config file, let's call them USERINFO and SERVERCONFIG
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
        "stock1": "ABBOTT LABORATORIES",
        "time1": "5min",

        "stock2": "ABBVIE",
        "time2": "5min",

        "stock3": "ACCENTURE PLC.",
        "time3": "5min",

        "stock4": "ADOBE",
        "time4": "5min",

        "stock5": "ADVANCED MICRO DEVICES",
        "time5": "5min"
    }

    #Write the above sections to config.ini file
    with open('config.ini', 'w') as conf:
        config_object.write(conf)