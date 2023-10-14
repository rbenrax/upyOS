import gc
import micropython
import utls 

def __main__(args):

    An=const("\033[0m")
    Ab=const("\033[1m")
    
    mod=""
    if len(args) > 0: mod=args[0]
    
    if mod=="--h":
        print("Show ram status\nUsage: df <options>: --h -h -p")
        return

    gc.collect()
    
    f = gc.mem_free()
    a = gc.mem_alloc()
    t = f+a
    p = f'({f/t*100:.2f}%)'
    s = micropython.stack_use()
    
    if mod=="-p":
        d={"Total": t, "Alloc": a, "Free": f, "%": p, "Stack": s}
        utls.setenv("0", d)
        
    elif mod == "-h":
        print(f'{An}Total: {Ab}{utls.human(t)}')
        print(f'{An}Alloc: {Ab}{utls.human(a)}')
        print(f'{An}Free.: {Ab}{utls.human(f)} {p}')
        print(f'{An}Stack: {Ab}{utls.human(s)}{An}')
        
    else:
        print(f'{An}Total: {Ab}{t:7} bytes')
        print(f'{An}Alloc: {Ab}{a:7} bytes')
        print(f'{An}Free.: {Ab}{f:7} bytes {p}')
        print(f'{An}Stack: {Ab}{s:7} bytes{An}')


