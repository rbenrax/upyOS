# Asyncio Test 
# From command line launch with & ending

import uasyncio
import machine
import sys

# Current process refeference (passed in call)
proc=None

from _thread import get_ident

async def blink(led, period_ms):
    while True:
        
        if proc.sts=="S":break

        led.on()
        await uasyncio.sleep_ms(5)
        led.off()
        await uasyncio.sleep_ms(period_ms)

async def main():
    if sys.platform=="esp32":
        t1 = uasyncio.create_task(blink(machine.Pin(12), 700))
    else:
        t1 = uasyncio.create_task(blink(machine.Pin(25), 700))
    t2 = uasyncio.create_task(blink(machine.Pin(13), 100))
    #await t1
    #await t2
    # await uasyncio.sleep_ms(5000)
    results = await uasyncio.gather(t1, t2)

def __main__(args):
    #print(proc.syscall.user_commands)
    uasyncio.run(main())

if __name__ == "__main__":
    args =[""]
    __main__(args)
    
        
