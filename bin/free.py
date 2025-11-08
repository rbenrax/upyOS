import gc
import micropython
from utls import outs, human

def __main__(args):
    
    mod = args[0] if args else ""
    
    if "--h" in mod:
        print("Show ram status\nUsage: free <options>: --h -h [>[>] var/file]")
        return
    
    gc.collect()
    
    f = gc.mem_free()
    a = gc.mem_alloc()
    t = f + a
    s = micropython.stack_use()
    
    ret = {"Total": t, "Alloc": a, "Free": f, "%": f"{f/t*100:.2f}%", "Stack": s}
    
    if outs(args, ret, False):    
        return
    
    # Usar secuencias ANSI directamente en lugar de variables
    if mod == "-h":
        print(f'\033[0mTotal: \033[1m{human(t)}')
        print(f'\033[0mAlloc: \033[1m{human(a)}')
        print(f'\033[0mFree.: \033[1m{human(f)} ({f/t*100:.2f}%)')
        print(f'\033[0mStack: \033[1m{human(s)}\033[0m')
    else:
        print(f'\033[0mTotal: \033[1m{t:7} bytes')
        print(f'\033[0mAlloc: \033[1m{a:7} bytes')
        print(f'\033[0mFree.: \033[1m{f:7} bytes ({f/t*100:.2f}%)')
        print(f'\033[0mStack: \033[1m{s:7} bytes\033[0m')
