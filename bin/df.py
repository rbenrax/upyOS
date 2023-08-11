import sys
import sdata
import uos

"""Show ram status"""
def __main__(args):

    mode=""
    path="/"

    if len(args) == 1:
        mode=args[0]
    elif len(args) == 2:
        mode=args[0]
        path=args[1]
    
    if mode == "-h":
        print("df <options>, options -h -p")
        return
    
    bit_tuple = uos.statvfs(path)
    blksize = bit_tuple[0]  # system block size
    t = bit_tuple[2] * blksize
    f = bit_tuple[3] * blksize
    u = t - f

    if mode=="-p":
        d={"total": t, "used": u, "free": f}
        print(d) 
    else:
        print(f'\033[0mTotal space:\033[1m {t:8} bytes')
        print(f'\033[0mUsed space.:\033[1m {u:8} bytes')
        print(f'\033[0mFree space.:\033[1m {f:8} bytes\033[0m')
    
if __name__ == "__main__":
    args =[""]
    __main__(args)
        