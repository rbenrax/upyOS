# Asyncio Test 
# From command line launch with & ending

import sdata
import uasyncio
from machine import Pin
import _thread

async def blink(led, period_ms):
    while True:

        #if sdata.getenv("THR1") !="R": break
        pid_sts="R"
        thid = _thread.get_ident()
        for i in sdata.procs:
            if isinstance(i, str): continue
            print(f"{i.pid} {i.tid} {i.cmd} {i.args}")
            if i.tid == thid:
                pid_sts=i.sts
                break
                
        if pid_sts != "R": break

        led.on()
        await uasyncio.sleep_ms(5)
        led.off()
        await uasyncio.sleep_ms(period_ms)

async def main():    
    t1 = uasyncio.create_task(blink(Pin(25), 700))
    t2 = uasyncio.create_task(blink(Pin(13), 100))
    #await t1
    #await t2
    # await uasyncio.sleep_ms(5000)
    results = await uasyncio.gather(t1, t2)

def __main__(args):
    uasyncio.run(main())

if __name__ == "__main__":
    args =[""]
    __main__(args)
    
        
