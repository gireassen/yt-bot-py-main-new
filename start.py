import functions
import time


dt = int(time.time() * 1000)    #текущая дата
#dt = (int(time.time()) * 1000 + 2000)    #текущая дата
print(dt)
#timestamp = (dt - 1000000)
functions.write_file_time(dt)

