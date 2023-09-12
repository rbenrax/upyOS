import sdata
from machine import freq

def __main__(args):

    if len(args) != 1 or args[0] == "--h":
        print("Set clock speed\nUsage: cpuclock <option>: -low, -turbo, <freq> (caution), --h -v")
        return

    if args[0] == "-v":
        print(f"CPU speed: {freq()*0.000001} MHz")
        return

    if "mcu" in sdata.board:
        if args[0] == "-low":
            f = sdata.board["mcu"][0]["speed"]["slow"]

        if args[0] == "-turbo":
            f = sdata.board["mcu"][0]["speed"]["turbo"]
    else:
        print(f"Invalid modificator, no board file configuration")
        
    if args[0].isdigit():
        f = int(args[0])
        
    try:
        freq(f * 1000000)
        print("CPU speed set to " + str(f) + " Mhz")
    except ValueError as ve:
        print(ve)
        
        

        
