import sys
import sdata
import gc

"""Show ram status"""
def __main__(args):

    if len(args) == 1:
        mode=args[0]
    else:
        mode=""

    if mode == "-h":
        print("df <options>, options -h -p")
        return
    
    gc.collect()
    
    f = gc.mem_free()
    a = gc.mem_alloc()
    t = f+a
    p = f'({f/t*100:.2f}%)'
    
    if mode=="-p":
        d={"total": t, "alloc": a, "free": f, "%": p}
        print(d)
    else:
        print(f'\033[0mTotal.:\033[1m {t:7} bytes')
        print(f'\033[0mAlloc.:\033[1m {a:7} bytes')
        print(f'\033[0mFree..:\033[1m {f:7} bytes {p}\033[0m')

    #del sys.modules["gc"]
    
if __name__ == "__main__":      
    __main__("-h")
        