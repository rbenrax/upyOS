#import utls

def __main__(args):
    if len(args) > 0:
#        for i, a in enumerate(args):
#            if a[0]=="$":
#                args[i] = utls.getenv(a[1:])
        print("".join(args))
    else:
        print("Show msg + env variable\nUsage: echo const/<var>: var $?, $1, ..., any")
