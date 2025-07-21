from datetime import datetime
from zoneinfo import ZoneInfo

print(datetime.now())
print(datetime.now(ZoneInfo('US/Eastern')))
now_et = datetime.now(ZoneInfo('US/Eastern'))

now_hhmmss_int = int(now_et.strftime('%H%M%S'))

print(now_hhmmss_int)
print(type(now_hhmmss_int))