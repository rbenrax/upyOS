import uos
import machine
import sdata

def __main__(args):

    if len(args) < 1:
        print ("List system hardware and interfaces\nUsage: lshw <options>, options: -b, -f")
        return

    mode=args[0]
    name = uos.uname()[0]

    print(f"\033[0mBoard:\033[1m {uos.uname()[4]}")
    print(f"\033[0mMicroPython:\033[1m {uos.uname().release}")
    print(f"\033[0m{sdata.name} :\033[1m {sdata.version} (size: {uos.stat('/lib/kernel.py')[6]} bytes)")
    print(f"\033[0mFirmware:\033[1m{uos.uname().version}")

    if sdata.sysconfig["turbo"]:
        turbo_msg = "\033[0mIn \033[1mturbo mode\033[0m. Use `turbo` for slow mode."
    else:
        turbo_msg = f"\033[0mIn power-saving, \033[1mslow mode\033[0m. Use `cpufreq` command to set speed."
    
    print(f"\033[0mCPU Speed:\033[1m{machine.freq()*0.000001}MHz {turbo_msg}")

    # Full hardware
    if mode=="-f":
        try:
            for e in sdata.board.keys():
                i=sdata.board[e]
                #TODO prettify
                #print(f"{type(i)}")
                #if type(i) is dict:
                #    print(f"{e}: {i}")
                #if type(i) is list:
                #    print(f"{e}: {i}")
                #else:
                #    print(f"{e}: {i}")
                    
                print(f"{e}: {i}")

        except Exception as ex:
            print("lshw error, " + str(ex))
            pass

#if __name__ == '__main__':
#    __main__("-f")
