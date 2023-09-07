# Asyncio Test 
# From command line launch with & ending

import sdata
import uasyncio
import machine

# The user space functions can avoid module being removed (passed in call)
rmmod=False

# The user space functions can call system funcions by syscall reference (passed in call)
syscall=None

from _thread import get_ident

async def blink(led, period_ms):
    while True:
        
        if sdata.endthr(get_ident()): break

        led.on()
        await uasyncio.sleep_ms(5)
        led.off()
        await uasyncio.sleep_ms(period_ms)

async def main():    
    t1 = uasyncio.create_task(blink(machine.Pin(25), 700))
    t2 = uasyncio.create_task(blink(machine.Pin(13), 100))
    #await t1
    #await t2
    # await uasyncio.sleep_ms(5000)
    results = await uasyncio.gather(t1, t2)

def __main__(args):
    print(syscall.user_commands)
    uasyncio.run(main())

if __name__ == "__main__":
    args =[""]
    __main__(args)
    
        
