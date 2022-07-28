# Import datetime class from the datetime module
from datetime import datetime as dtInner

# Function to synchronise 5 minute timing
def syncTiming5():
     # Get the current time as string
     now = str(dtInner.now())
     # Split string by colon
     splitNow = now.split(":")
     # Get minutes and seconds as ints from split list by typecasting
     minutes = int(splitNow[1])
     seconds = round(float(splitNow[2]))
     # Check if minutes is already a multiple of 5 or a new hour
     if minutes % 5 == 0:
          # Return 5 minutes + 1 second in seconds
          return 301
     else:
          # Initialize counter
          min2 = minutes
          counter = 0
          # While min2 is not divisible by 5
          while min2 % 5 != 0:
               # Increment
               min2 += 1
               counter += 1
          # Calculate seconds to wait by multiplying the minutes until the time is divisible by 5 by 60, then subtracting the remaining seconds and adding 1
          actualSeconds = ((counter * 60) - seconds) + 1
          return(actualSeconds)

# Function to sync 30min interval
def syncTiming30():
     now = str(dtInner.now())
     splitNow = now.split(":")
     minutes = int(splitNow[1])
     seconds = round(float(splitNow[2]))
     # If current minutes are already 30 mins or an hour
     if minutes == 30 or minutes == 0:
          # Return 30 mins + 1 second
          return 1801
     else:
          # If minutes is less than 30
          if minutes < 30:
               # Set difference to 30 minus minutes
               diff = 30 - minutes
          else:
               # Else set difference to hour minus minnutes
               diff = 60 - minutes
     # Calculate seconds to wait
     actualSeconds = ((diff * 60) - seconds) + 1
     return(actualSeconds)

# Function to sync timing with 1 hour interval
def syncTiming60():
     now = str(dtInner.now())
     splitNow = now.split(":")
     minutes = int(splitNow[1])
     seconds = round(float(splitNow[2]))
     # If current time is an hour
     if minutes == 0:
          # Return 1 hour in seconds + 1
          return 3601
     else:
          # Else calculate an hour - minutes to get the difference
          diff = 60 - minutes
     # Calculate and return seconds + 1
     actualSeconds = ((diff * 60) - seconds) + 1
     return(actualSeconds)