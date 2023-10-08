import ntptime

import utls

proc=None

def __main__(args):

    if len(args) == 0:
        print("Update time from NTP server\nUsage: updatentp <ntp server ip>")
        return
    
    try:
        
        offset = int(proc.syscall.getenv("TZ"))
        
        ntptime.host = args[0]
        ntptime.settime()
        #ntptime.settime(timezone=2, server = args[0]) # doesnt work

        from machine import RTC
        rtc = RTC()
        date_time = list(rtc.datetime())
        date_time[4] = date_time[4] + offset # TODO: not fine, looks for a better solution 
        date_time = tuple(date_time)
        rtc.datetime(date_time)
        
    except Exception as ex:
        print("ntpupdate error: ", ex)
        
        
        

        
