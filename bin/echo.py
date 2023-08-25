import sdata

def __main__(args):
    if len(args) > 0:
        ret=""
        for a in args:
            val = sdata.getenv(a)
            if val=="":
                ret += a + " "
            else:
                ret += val + " "
                
        print(ret[:-1])
        return(ret[:-1])
    else:
        print("Show msg + env variable, echo const/<var>: var $?, $1, ..., any")
