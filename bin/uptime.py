import utime
import sdata

localt = utime.gmtime(utime.time())
uptime = utime.gmtime(utime.time() - (sdata.initime))

print (f"{localt[3]:0>2} {localt[4]:0>2} {localt[5]:0>2}  {uptime[3]:0>2} {uptime[4]:0>2} {uptime[5]:0>2} up")
