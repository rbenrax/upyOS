import utime
import sdata

#TODO: Revise time
localtime = utime.localtime(utime.time())
print (f"Current time from system startup is: {localtime[2]:0>2} {localtime[4]:0>2} {localtime[5]:0>2}")

       