import uos
import machine
import utls

import sdata
import sys

def __main__(args):

    if len(args) == 1 and args[0]=="--h":
        print ("List system hardware and interfaces\nUsage: lshw <options>, options: -f [cat]")
        return
    
    if len(args)==0:
        mode="-b"
    else:
        mode=args[0]
        
    name = uos.uname()[0]

    # ansi macros, or somethin like that!
    from micropython import const
    An=const("\033[0m")
    Ab=const("\033[1m")
    
    print(f"{An}SystemID:{Ab} {sdata.sid}")
    print(f"{An}Platform:{Ab} {sys.platform}")
    print(f"{An}Board:{Ab} {uos.uname()[4]}")
    print(f"{An}{sdata.name} :{Ab} {sdata.version}")
    print(f"{An}MicroPython:{Ab} {uos.uname().release}")
    print(f"{An}Firmware:{Ab} {uos.uname().version}")
    print(f"{An}CPU Speed:{Ab} {machine.freq()*0.000001}MHz{An}")
    
    # Full hardware
    if mode=="-f":
        
        if not sdata.board:
            print ("lshw -f: This board has no hardware configuration defined")
            return   
        
        def plist(l, p=1):
            for v in l:
                print("\t"*p + f"{Ab}{v}")
                
        def pdict(d, p=1):
            k = list(d.keys())
            
            if all(e.isdigit() for e in k):
                k.sort(key=int)
            else:
                k.sort()
                
            for i in k:
                #print("\t"*p +f"{An}{i} : {Ab}{d[i]}")
                print("\t"*p +f"{An}{i} \t: {Ab}{d[i]}")
                #print("\t"*p + f"{An}{utls.tspaces(i, n=7)} : {Ab}{d[i]}")
                
        def pboard(e):
            
            if not e in sdata.board: return
            
            i=sdata.board[e]
            #print(type(i))
            print("")
            if isinstance(i, list):
                
                if len(i) > 0 and not isinstance(i[0], list) and not isinstance(i[0], dict):
                    print(f"{An}{e}:")
                    plist(i, p=1)
                    return
                
                for n, j in enumerate(i):
                    if len(i) > 1:
                        print(f"{An}{e}[{n}]: ")
                    else:
                        print(f"{An}{e}: ")
                        
                    if isinstance(j, dict):
                        pdict(j, 1)
                    elif isinstance(j, list):
                        plist(j, 1)
                    else:
                        print(f"{Ab}{j}")

            elif isinstance(i, dict):
                print(f"{An}{e}: ")
                pdict(i, 1)
            else:
                print(f"{An}{e}:\t{Ab}{i}")
        
        
        try:
            
            print(f"\n{Ab}Board hardware interfaces, pinout and gpios descriptions{An}")
            
            if len(args)>1:
                pboard(args[1])
            else:
            
                top=["board","mcu","eth","wifi","bt","ir","rtc","temp","ver","text"]
                bottom=["5v0","3v3","gnd","nc","other"]
                
                for e in top:
                    if e in bottom: continue
                    pboard(e)  
                
                for e in sdata.board.keys():
                    if e in top or e in bottom: continue
                    pboard(e)
                
                for e in bottom:
                    pboard(e)
                
                print(f"{An}\nEnd of hardware definitions")
            
        except Exception as ex:
            print("lshw error, " + str(ex))
            sys.print_exception(ex)
            pass

#if __name__ == '__main__':
#    __main__("-f")
