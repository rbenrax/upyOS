import sdata
from machine import freq

def __main__(args):

    if len(args) != 1 or args[0] == "--h":
        print("Set clock speed, cpuclock set <option>: -low, -turbo, --h -v -t (toggle)")
        return

    actclk = sdata.sysconfig["turbo"]
    newclk = False
    
    if args[0] == "-v":
        print("Turbo CPU speed: " + str(actclk))
        return
    
    if args[0] == "-t":
        newclk = not actclk

    if args[0] == "-low" or newclk == False :
        f = sdata.board["mcu"][0]["speed"]["slow"]

    if args[0] == "-turbo" or newclk == True :
        f = sdata.board["mcu"][0]["speed"]["turbo"]
        
    sdata.sysconfig["turbo"] = newclk
    freq(f * 1000000)
    print("CPU speed set to " + str(f) + " Mhz")
        
if __name__ == "__main__":

    args =["-low"]
    __main__(args)
        
