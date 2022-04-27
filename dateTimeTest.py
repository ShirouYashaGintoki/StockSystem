from datetime import datetime

def getTime():
    now = str(datetime.now())
    splitNow = now.split(":")
    minutes = int(splitNow[1])
    seconds = int(float(splitNow[2]))
    if minutes == 30 or minutes == 0:
        if seconds > 30:
            return 31
        else:
            return 30
    else:
        counter = 0
        min2 = minutes
        while min2 != 30 or min2 != 0:
            min2 += 1
            counter +=1
            if min2 == 60:
                break
            print(str(min2), str(counter))
        if seconds > 30:
            counter += 1
        return counter

print(getTime())