import datetime
import time

d1 = datetime.datetime.now()
time.sleep(0.25)
d2 = datetime.datetime.now()
print(d2 - d1)