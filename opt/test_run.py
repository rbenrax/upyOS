import sdata
import sys

def __main__(args):
    print(f"{args=} {sdata.sysconfig["env"]}")
    if len(args) > 0:
        ret=""
        for a in args[1:]:
            val = sdata.getenv(a)
            if val=="":
                ret += a + " "
            else:
                ret += val + " "
                
        print(ret[:-1])
        return(ret[:-1])
    else:
        print("Show env variable, echo const/<var>: var $?, $1, ..., any")

#print(__name__)
#if __name__ == "builtins":
#print(dir())
#print(args)
#args = sys.argv[1:]
__main__(args)
