import machine
import utime
import sdata
import sys

def __main__(args):

    if len(args) < 2:
        print ("Usage:")
        print ("Control system leds\nUsage: led <command> <led>: on, off led: 1,..., rgb led in strip ")
        return

    if not sdata.board:
        print("Unknown board, this board has not a .board file loaded, see /etc/init.sh")
        return 

    cmd=args[0]
    ln=int(args[1])

    # Test rgb leds gpios with ln leds in each strip
    if cmd=="rgb":
        if not "rgbio" in sdata.board:
            return
        
        if ln < 1: return
        import neopixel
        for pn in sdata.board["rgbio"][0].values():
            try:
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
            except Exception as ex:
                print("Warning: (rgbio) Possibly a bad .board file in loadboard command. See /etc/init.sh")
                return False
        
        np=None
        del sys.modules["neopixel"]
        return

    system_leds = []
    if "ledio" in sdata.board and len(sdata.board["ledio"][0]) > 0:
    
        try:
            for pn in sdata.board["ledio"][0].values(): #Leds gpios
               system_leds.append(machine.Pin(pn, machine.Pin.OUT))
               
        except Exception as ex:
            print("Warning: (ledio) Possibly a bad .board file in loadboard command. See /etc/init.sh")
            return False

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
