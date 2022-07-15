from configparser import ConfigParser
import mainGUI_clean

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

def saveConfig():
     config_object = ConfigParser()
     config_object.read("config.ini")

     configData = config_object["STOCKCONFIG"]

     configData["stock1"] = mainGUI_clean.clicked1.get()
     configData["time1"] = mainGUI_clean.timeFrame1.get()

     configData["stock2"] = mainGUI_clean.clicked2.get()
     configData["time2"] = mainGUI_clean.timeFrame2.get()

     configData["stock3"] = mainGUI_clean.clicked3.get()
     configData["time3"] = mainGUI_clean.timeFrame3.get()

     configData["stock4"] = mainGUI_clean.clicked4.get()
     configData["time4"] = mainGUI_clean.timeFrame4.get()

     configData["stock5"] = mainGUI_clean.clicked5.get()
     configData["time5"] = mainGUI_clean.timeFrame5.get()

     with open('config.ini', 'w') as conf:
          config_object.write(conf)
     conf.close()
     print("Config written to!")

def loadConfig():
     config_object = ConfigParser()
     config_object.read("config.ini")

     configData = config_object["STOCKCONFIG"]
     mainGUI_clean.clicked1.set(configData["stock1"])
     mainGUI_clean.timeFrame1.set(configData["time1"])

     mainGUI_clean.clicked2.set(configData["stock2"])
     mainGUI_clean.timeFrame2.set(configData["time2"])

     mainGUI_clean.clicked3.set(configData["stock3"])
     mainGUI_clean.timeFrame3.set(configData["time3"])

     mainGUI_clean.clicked4.set(configData["stock4"])
     mainGUI_clean.timeFrame4.set(configData["time4"])

     mainGUI_clean.clicked5.set(configData["stock5"])
     mainGUI_clean.timeFrame5.set(configData["time5"])
