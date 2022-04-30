from datetime import datetime

now = datetime.now()
splitnow = str(now).split(":")

minutes = splitnow[1]
secondsround = round(float(splitnow[2]))