import ntptime
import utime

proc=None

def __main__(args):

    if len(args) == 0:
        print("Update system time from NTP server\nUsage: ntpupdate <ntp server ip>")
        return
    
    try:
        
        tz = int(proc.syscall.getenv("TZ"))
        
        ntptime.host = args[0]
        ntptime.settime()

        from machine import RTC
        rtc = RTC()
        
        ## --- M1
        y, mo, d, _, h, m, s, _ = rtc.datetime()
        
        # Calcular el desplazamiento en segundos
        offset = tz * 3600
        
        # Sumar el desplazamiento a la hora actual
        nh = h + (offset // 3600)
        nm = m + ((offset % 3600) // 60)
        ns = s + (offset % 60)
        
        # Asegurarse de que la nueva hora, minuto y segundo estén en rangos válidos
        nh = nh % 24
        nm = nm % 60
        ns = ns % 60
        
        # Configurar la nueva fecha y hora en el RTC
        #print(f"P1{y} {mo} {d} {nh} {nm} {ns}")
        rtc.datetime((y, mo, d, 0, nh, nm, ns, 0))
        
        del sys.modules["ntptime"]
        
        ## --- M2 (not fine)
        #date_time = list(rtc.datetime())
        #date_time[4] = date_time[4] + offset 
        #date_time = tuple(date_time)
        ##print(f"P1{date_time}")
        #rtc.datetime(date_time)
        
        # --- M3 (Bad)
        #sec = utime.mktime(rtc.datetime())
        #sec = utime.mktime(utime.localtime())
        #sec = sec + (tz * 3600)
        #y, mo, d, _, h, m, s, _ = utime.gmtime(sec)
        ##print(f"P1: {y} {mo} {d} {h} {m} {s}")
        #rtc.datetime((y, mo, d, 0, h, m, s, 0))
        
    except Exception as ex:
        print("ntpupdate error: ", ex)
