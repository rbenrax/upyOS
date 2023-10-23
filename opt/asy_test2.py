# Asyncio Test 
# From command line launch with & ending

import uasyncio
import machine
import sys
import utime
import neopixel
import random

import sdata

# Current process refeference (passed in call)
proc=None

async def blink(np, period_ms):
    while True:
        
        if proc.sts=="S":break
        
        if proc.sts=="H":
            #utime.sleep(1)
            await uasyncio.sleep(1)
            continue

        c1=random.randint(0, 128)
        c2=random.randint(0, 128)
        c3=random.randint(0, 128)
        
        np[0] = (c1, c2, c3, 5)
        np.write()
        await uasyncio.sleep_ms(period_ms)
        np[0] = (0, 0, 0, 5)
        np.write()

async def main():

    if len(sdata.board["rgbio"])>0:
        lp = list(sdata.board["rgbio"][0].values())
        #print(lp[0])
        
        np = neopixel.NeoPixel(machine.Pin(lp[0]), 1, bpp=4)
        
        t1 = uasyncio.create_task(blink(np, 400))
        t2 = uasyncio.create_task(blink(np, 700))
        #await t1
        #await t2
        #await t3
        # await uasyncio.sleep_ms(5000)
        results = await uasyncio.gather(t1, t2)

def __main__(args):
    #print(proc.syscall.user_commands)
    uasyncio.run(main())

if __name__ == "__main__":
    args =[""]
    __main__(args)
    
        
