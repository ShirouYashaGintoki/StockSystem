from datetime import datetime

def getTime():
    now = str(datetime.now())
    splitNow = now.split(":")
    minutes = int(splitNow[1])
    seconds = int(float(splitNow[2]))
    if minutes < 30:
        setTime = 30 - minutes
        if abs(seconds) > 30:
            setTime+=1
            if setTime > 30:
                setTime = 60 - minutes
                return setTime
            return setTime
        return setTime
    else:
        setTime = 60 - minutes
        if abs(seconds) > 30:
            setTime += 1
            return setTime
        return setTime

print(getTime())