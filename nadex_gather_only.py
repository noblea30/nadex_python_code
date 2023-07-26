#just gather the data.  For now, keep high/low/ind,etc.


from calculations import *
from drivers import *
from time import sleep
import time

open_browser(url, profile, path, headless)


login_real()

#time.sleep(3)
t = get_time()
#t = convert_time_to_epoch(t_str)
print(t)

open_stocks()
t1 = time.time()
while 1:
   for i in range(1):  #this loop is just for keep awake.
      t1 = time.time()
      data = check_prices()
      
      save_data(data)
      print(time.time()-t1)
   keep_awake_fast()
   #time.sleep(2)