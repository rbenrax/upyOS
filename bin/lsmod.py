import sys
import utls
import sdata

def __main__(args):
    
    for k , v in sys.modules.items():
        print(f"{utls.tspaces(k, 12, "a")}{v}")
