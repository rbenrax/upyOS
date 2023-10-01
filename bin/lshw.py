import uos
import machine
import sdata
import sys

def __main__(args):

    if len(args) == 1 and args[0]=="--h":
        print ("List system hardware and interfaces\nUsage: lshw <options>, options: -f")
        return
    
    mode=args[0]
    name = uos.uname()[0]

    print(f"\033[0mSystemID:\033[1m {sdata.sid}")
    print(f"\033[0mPlatform:\033[1m {sys.platform}")
    print(f"\033[0mBoard:\033[1m {uos.uname()[4]}")
    print(f"\033[0m{sdata.name} :\033[1m {sdata.version} (size: {uos.stat('/lib/kernel.py')[6]} bytes)")
    print(f"\033[0mMicroPython:\033[1m {uos.uname().release}")
    print(f"\033[0mFirmware:\033[1m{uos.uname().version}")
    print(f"\033[0mCPU Speed:\033[1m{machine.freq()*0.000001}MHz")
    
    def plist(l, p=1):
        for v in l:
            print("\t"*p + f"{v}")
            
    def pdict(d, p=1):
        for k, v in d.items():
            print("\t"*p +f"{k} : {v}")

    def pboard(e):
        i=sdata.board[e]
        #print(type(i))
        if isinstance(i, list):
            
            if len(i) > 0 and not isinstance(i[0], list) and not isinstance(i[0], dict):  
                print(f"{e}:")
                plist(i, p=1)
                return
            
            for n, j in enumerate(i):
                if len(i) > 1:
                    print(f"{e}{n}: ")
                else:
                    print(f"{e}: ")
                #print(f"Lista: {j}\n")
                if isinstance(j, dict):
                    pdict(j, 1)
                elif isinstance(j, list):
                    plist(j, 1)
                else:
                    print(f"{j}")

        elif isinstance(i, dict):
            print(f"{e}: ")
            pdict(i, 1)
        else:
            print(f"{e}: {i}")

    # Full hardware
    if mode=="-f":
        try:
            
            print(f"\033[0m\nPinout descrition of hardware interfaces\n")
            
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
            
        except Exception as ex:
            print("lshw error, " + str(ex))
            sys.print_exception(ex)
            pass

#if __name__ == '__main__':
#    __main__("-f")
