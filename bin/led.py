import machine
import utime
import sdata
import sys

def __main__(args):

    if len(args) < 2:
        print ("Usage:")
        print ("Control system leds\nUsage: led <command> <led>: on, off led: 0,1,..., rgb led in strip ")
        return

    cmd=args[0]
    ln=int(args[1])

    # Test rgb leds gpios with ln leds in each strip
    if cmd=="rgb":
        if not sdata.board or not "rgbio" in sdata.board:
            #print ("led: This board has no rgbio pin(s) defined")
            return
        
        if ln < 1: return
        import neopixel
        
        for pn in sdata.board["rgbio"][0].values():
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
        np=None
        del sys.modules["neopixel"]
        return

    if not sdata.board or not "ledio" in sdata.board:
        #print ("led: This board has no ledio pin(s) defined")
        return 

    system_leds = []
    if "ledio" in sdata.board:
        for pn in sdata.board["ledio"][0].values(): #Leds gpios
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

if __name__ == "__main__":

    args =["rgb", "1"]
    __main__(args)

