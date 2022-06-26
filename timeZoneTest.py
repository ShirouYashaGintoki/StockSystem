from datetime import datetime as dtInner
from dateutil import tz
import pytz
# dt_str  = "10/21/2021 8:18:19"
other_string = '2022-06-22 15:55:00'
format = "%Y-%m-%d %H:%M:%S"
ukFormat = "%d-%m-%Y %H:%M:%S"
local_zone = tz.tzlocal()
# format = "%d%m%Y %H:%M:%S"
# Create datetime object in local timezone
# dt_utc = datetime.strptime(dt_str, format)

def convertTz(tzString):
    dt_utc = dtInner.strptime(other_string, format)
    dt_utc = dt_utc.replace(tzinfo=pytz.UTC)
    dt_local = dt_utc.astimezone(local_zone)
    local_time_str = dt_local.strftime(ukFormat)
    return local_time_str

# dt_utc = dtInner.strptime(other_string, format)
# dt_utc = dt_utc.replace(tzinfo=pytz.UTC)
# print('Datetime in UTC Time zone: ', dt_utc)
# # Get local timezone
# local_zone = tz.tzlocal()
# # Convert timezone of datetime from UTC to local
# dt_local = dt_utc.astimezone(local_zone)
# print('Datetime in Local Time zone: ', dt_local)
# local_time_str = dt_local.strftime(ukFormat)
# print('Time as string in Local Time zone: ', local_time_str)

print(convertTz(other_string))