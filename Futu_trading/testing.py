import datetime

now_datetime = datetime.datetime.now()
now_weekday = now_datetime.weekday()
now_hhmmss_int = int(now_datetime.strftime('%H%M%S'))

print(now_datetime)
print(now_weekday)
print(now_hhmmss_int)
print(type(now_hhmmss_int))

