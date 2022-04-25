from datetime import datetime

now = str(datetime.now())
splitNow = now.split(":")

print(now)
print(splitNow)
minutes = int(splitNow[1])
seconds = int(float(splitNow[2]))



