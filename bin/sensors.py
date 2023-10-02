import sys
import sdata

def __main__(args):

    if len(args) == 1 and args[0] == "--h":
        print("Show system sensors\nUsage: sensors <option>: , --h")
        return

    try:
        if "temp" in sdata.board and sdata.board["temp"]:
            if sys.platform=="esp32":
                import esp32
                tf = esp32.raw_temperature()
                tc = (tf-32.0)/1.8
                print(f"Temp: {tf:d}F/{tc:.1f}C")
    except ValueError as ve:
        print(ve)
        
        

        
