import utime

import utls

localt = utime.gmtime(utime.time())
print (f"{utls.WEEKDAY[localt[6]]} {localt[2]:0>2}/{utls.MONTH[localt[1]]}/{localt[0]:0>4} {localt[3]:0>2}:{localt[4]:0>2}:{localt[5]:0>2}")



