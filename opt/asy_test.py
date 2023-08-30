
# Asyncio Test 
# From command line launch with & ending

#import sdata
import uasyncio
from machine import Pin

async def blink(led, period_ms):
    while True:
        led.on()
        await uasyncio.sleep_ms(5)
        led.off()
        await uasyncio.sleep_ms(period_ms)

async def main():    
    t1 = uasyncio.create_task(blink(Pin(12), 700))
    t2 = uasyncio.create_task(blink(Pin(13), 100))
    #await t1
    #await t2
    await uasyncio.sleep_ms(5000)
    #results = await uasyncio.gather(t1, t2)

def __main__(args):
    uasyncio.run(main())

if __name__ == "__main__":
    args =[""]
    __main__(args)
    
        