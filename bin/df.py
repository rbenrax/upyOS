import uos
import utls

def __main__(args):

    An=const("\033[0m")
    Ab=const("\033[1m")

    mod=""
    if len(args) > 0: mod=args[0]
    
    if mod=="--h":
        print("Show storage status\nUsage: df <options>: options --h -h -p")
        return

    path="/"
    if len(args) > 1: path=args[1]
        
    bit_tuple = uos.statvfs(path)
    blksize = bit_tuple[0]  # system block size
    
    t = bit_tuple[2] * blksize
    f = bit_tuple[3] * blksize
    u = t - f
    p = f'({f/t*100:.2f}%)'

    if mod=="-p":
        d={"total": t, "used": u, "free": f}
        utls.setenv("0", d)
        
    elif mod=="-h":
        print(f'{An}Total space: {Ab}{utls.human(t)}')
        print(f'{An}Used space.: {Ab}{utls.human(u)}')
        print(f'{An}Free space.: {Ab}{utls.human(f)} {p}{An}')
        
    else:
        print(f'{An}Total space: {Ab}{t:8} bytes')
        print(f'{An}Used space.: {Ab}{u:8} bytes')
        print(f'{An}Free space.: {Ab}{f:8} bytes {p}{An}')

