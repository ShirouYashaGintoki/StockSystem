from datetime import datetime
import time

now = datetime.now()
splitnow = str(now).split(":")

minutes = int(splitnow[1])
secondsround = round(float(splitnow[2]))

print(f'Minutes: {str(minutes)}')
print(f'Seconds: {str(secondsround)}')

min2 = minutes

global _5counter
_5counter = 0

if minutes < 30:
    diff = 30 - minutes
else:
    diff = 59 - minutes

# while min2 % 5 != 0:
#     min2 += 1
#     _5counter += 1

print(str(diff))

actualSeconds = ((diff * 60) - secondsround) + 1

print(f'Total seconds to wait: {str(actualSeconds)}')

if actualSeconds > 0:
    time.sleep(actualSeconds)
    print(datetime.now())
else:
    print("Either 0 or 5")