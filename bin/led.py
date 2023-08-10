import machine
import utime
import sdata

def __main__(args):

    if len(args) < 2:
        print ("Usage:")
        print ("led <command> <led number>, manipulating on-board LED. Commands: `on`, `off`, Led number: [0,1,...]",)
        return

    cmd=args[0]
    lna=args[1]
    ln=int(lna)

    # Test rgb leds gpios with ln leds in each strip
    if cmd=="rgb":
       if ln < 1: return
       import neopixel
       for pn in sdata.board["rgb"][0].values():
           np = neopixel.NeoPixel(machine.Pin(pn), ln, bpp=4)
           for i in range(ln):
               np[i] = (255, 0, 0, 5)
               np.write()                
               utime.sleep(.200)
               np[i] = (0, 255, 0, 5)
               np.write()                
               utime.sleep(.200)
               np[i] = (0, 0, 255, 5)
               np.write()                
               utime.sleep(.200)
               np[i] = (0, 0, 0, 0)
               np.write()
       return

    system_leds = []
    for pn in sdata.board["led"][0].values(): #Leds gpios
       system_leds.append(machine.Pin(pn, machine.Pin.OUT))

    if ln < 0 or ln>len(system_leds)-1:
       print("Led not found.")
       return
    if cmd in ("on",""):
       system_leds[ln].value(1)
       return
    if cmd=="off":
       system_leds[ln].value(0)
       return
    if cmd=="boot":
       for led in system_leds:
           for _ in range(2):
               led.value(1)
               utime.sleep(0.1)
               led.value(0)
               utime.sleep(0.05)
       return

