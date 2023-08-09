import sys
import sdata

#TODO: Prettify

def __main__(args):
    
    for k , v in sys.modules.items():
        print(f"{k}\t\t{v}")
