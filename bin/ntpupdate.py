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
        
        #date_time = list(rtc.datetime())
        #date_time[4] = date_time[4] + offset # TODO: not fine, looks for a better solution
        #date_time = tuple(date_time)
        #print(f"P1{date_time}")
        
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
        #print(f"P1{y} {m} {d}")
        rtc.datetime((y, mo, d, 0, nh, nm, ns, 0))
        
    except Exception as ex:
        print("ntpupdate error: ", ex)
        
        
        

        
