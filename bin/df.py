import uos
import utls

def __main__(args):
    
    mod = args[0] if args else ""
    
    if mod == "--h":
        print("Show storage status\nUsage: df <options>: options --h -h [>[>] var/file]")
        return
    
    path = args[1] if len(args) > 1 else "/"
    
    bit_tuple = uos.statvfs(path)
    blksize = bit_tuple[0]
    
    t = bit_tuple[2] * blksize
    f = bit_tuple[3] * blksize
    u = t - f
    
    ret = {"total": t, "used": u, "free": f, "%": f"{f/t*100:.2f}%"}
    
    if utls.outs(args, ret, False):
        return
    
    if mod == "-h":
        print(f'\033[0mTotal space: \033[1m{utls.human(t)}')
        print(f'\033[0mUsed space.: \033[1m{utls.human(u)}')
        print(f'\033[0mFree space.: \033[1m{utls.human(f)} ({f/t*100:.2f}%)\033[0m')
    else:
        print(f'\033[0mTotal space: \033[1m{t:8} bytes')
        print(f'\033[0mUsed space.: \033[1m{u:8} bytes')
        print(f'\033[0mFree space.: \033[1m{f:8} bytes ({f/t*100:.2f}%)\033[0m')
        