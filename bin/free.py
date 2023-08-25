import gc
import utls 

def __main__(args):

    mode=""
    if len(args) > 0:
        mode=args[0]

    if mode == "--h":
        print("Show ram status\nUsage: df <options>: --h -h -p")
        return
    
    gc.collect()
    
    f = gc.mem_free()
    a = gc.mem_alloc()
    t = f+a
    p = f'({f/t*100:.2f}%)'
    
    if mode=="-p":
        d={"total": t, "alloc": a, "free": f, "%": p}
        print(d)
    elif mode == "-h":
        print(f'\033[0mTotal.:\033[1m {utls.human(t)}')
        print(f'\033[0mAlloc.:\033[1m {utls.human(a)}')
        print(f'\033[0mFree..:\033[1m {utls.human(f)} {p}\033[0m')
    else:
        print(f'\033[0mTotal.:\033[1m {t:7} bytes')
        print(f'\033[0mAlloc.:\033[1m {a:7} bytes')
        print(f'\033[0mFree..:\033[1m {f:7} bytes {p}\033[0m')
    
if __name__ == "__main__":
    a=["-h"]
    __main__(a)
        
