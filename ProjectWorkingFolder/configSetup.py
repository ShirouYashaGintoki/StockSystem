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

def saveConfig(clicked1, clicked2, clicked3, clicked4, clicked5, timeFrame1, timeFrame2, timeFrame3, timeFrame4, timeFrame5):
    config_object = ConfigParser()
    config_object.read("config.ini")

    configData = config_object["STOCKCONFIG"]

    configData["stock1"]
    clicked1.get()
    configData["time1"]
    timeFrame1.get()

    configData["stock2"]
    clicked2.get()
    configData["time2"]
    timeFrame2.get()

    configData["stock3"]
    clicked3.get()
    configData["time3"]
    timeFrame3.get()

    configData["stock4"]
    clicked4.get()
    configData["time4"]
    timeFrame4.get()

    configData["stock5"]
    clicked5.get()
    configData["time5"]
    timeFrame5.get()

    with open('config.ini', 'w') as conf:
        config_object.write(conf)
        conf.close()
        print("Config written to!")

def loadConfig(clicked1, clicked2, clicked3, clicked4, clicked5, timeFrame1, timeFrame2, timeFrame3, timeFrame4, timeFrame5):
    config_object = ConfigParser()
    config_object.read("config.ini")

    configData = config_object["STOCKCONFIG"]
    clicked1.set(configData["stock1"])
    timeFrame1.set(configData["time1"])

    clicked2.set(configData["stock2"])
    timeFrame2.set(configData["time2"])

    clicked3.set(configData["stock3"])
    timeFrame3.set(configData["time3"])

    clicked4.set(configData["stock4"])
    timeFrame4.set(configData["time4"])

    clicked5.set(configData["stock5"])
    timeFrame5.set(configData["time5"])

    return clicked1, clicked2, clicked3, clicked4, clicked5, timeFrame1, timeFrame2, timeFrame3, timeFrame4, timeFrame5