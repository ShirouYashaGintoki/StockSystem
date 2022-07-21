from datetime import datetime as dtInner

# Function to synchronise timing with current time
def syncTiming5():
     # Get the current time as string
     now = str(dtInner.now())
     # Split string by colon
     splitNow = now.split(":")
     # Get minutes and seconds as ints from split list by typecasting
     minutes = int(splitNow[1])
     seconds = round(float(splitNow[2]))
     # Check if minutes is already a multiple of 5
     if minutes % 5 == 0:
          return 301
     else:
          min2 = minutes
          counter = 0
          while min2 % 5 != 0:
               min2 += 1
               counter += 1     
          actualSeconds = ((counter * 60) - seconds) + 1
          return(actualSeconds)

def syncTiming30():
     now = str(dtInner.now())
     splitNow = now.split(":")
     minutes = int(splitNow[1])
     seconds = round(float(splitNow[2]))
     if minutes == 30 or minutes == 0:
          return 1801
     else:
          if minutes < 30:
               diff = 30 - minutes
          else:
               diff = 59 - minutes
     actualSeconds = ((diff * 60) - seconds) + 1
     return(actualSeconds)

def syncTiming60():
     now = str(dtInner.now())
     splitNow = now.split(":")
     minutes = int(splitNow[1])
     seconds = round(float(splitNow[2]))
     if minutes == 30:
          return 3601
     else:
          if minutes < 30:
               diff = 30 - minutes
          else:
               diff = 59 - minutes
     actualSeconds = ((diff * 60) - seconds) + 1
     return(actualSeconds)