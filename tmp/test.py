import utls, sdata, uos, sys

def __main__(args):

    def print_mod(mod):
        try:
            print(f"{mod}:")
            m = __import__(mod)
            #for e in dir(m):
            #    print(f"\tAttr: {str(e)}")

            #print(sys.modules)
            del sys.modules[mod]
        except Exception as ex:
            print("Err: " + str(ex))
            pass
        
        print("")


#    print (f"Prueba de llamada {args}")
    #help("modules")
    try:
        #help("modules")
        
        #ls ="__main__          lwip              uasyncio/lock     upysh"
        #ls +="_boot             math              uasyncio/stream   urandom"
        #ls +="_onewire          micropython       ubinascii         ure"
        #ls +="_uasyncio         mip/__init__      ucollections      urequests"
        #ls +="_webrepl          neopixel          ucryptolib        urllib/urequest"
        #ls +="apa102            network           uctypes           uselect"
        #ls +="btree             ntptime           uerrno            usocket"
        #ls +="builtins          onewire           uhashlib          ussl"
        #ls +="dht               port_diag         uheapq            ustruct"
        #ls +="ds18x20           ssd1306           uio               usys"
        #ls +="esp               uarray            ujson             utime"
        #ls +="flashbdev         uasyncio/__init__ umachine          uwebsocket"
        #ls +="framebuf          uasyncio/core     umqtt/robust      uzlib"
        #ls +="gc                uasyncio/event    umqtt/simple      webrepl"
        #ls +="inisetup          uasyncio/funcs    uos               webrepl_setup"
        
        ls ="__main__          lwip                    upysh"
        ls +="_boot             math                 urandom"
        ls +="_onewire          micropython       ubinascii         ure"
        ls +="_uasyncio         mip      ucollections      urequests"
        ls +="_webrepl          neopixel          ucryptolib        urllib"
        ls +="apa102            network           uctypes           uselect"
        ls +="btree             ntptime           uerrno            usocket"
        ls +="builtins          onewire           uhashlib          ussl"
        ls +="dht               port_diag         uheapq            ustruct"
        ls +="ds18x20           ssd1306           uio               usys"
        ls +="esp               uarray            ujson             utime"
        ls +="flashbdev         uasyncio umachine          uwebsocket"
        ls +="framebuf               umqtt      uzlib"
        ls +="gc                          webrepl"
        ls +="inisetup              uos               webrepl_setup"
        
        nl = ls.split()
        #print(f"{nl=}")
        for e in nl:
            print_mod(e)


    except Exception as ex:
        print(ex)
        sys.print_exception(ex)
        pass


if __name__ == "__main__":

    args =["ls"]
    __main__(args)

        