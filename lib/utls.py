# Utility functions

import utime
from uos import stat
from uos import getcwd
from json import dump as jdump
from json import load as jload

import sdata

MONTH = ('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
WEEKDAY = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')

def file_exists(filename):
    return get_mode(filename) & 0xc000 != 0

def isdir(filename):
    return get_mode(filename) & 0x4000 != 0

def isfile(filename):
    return get_mode(filename) & 0x8000 != 0

def get_mode(filename):
    try:
        return stat(filename)[0]
    except OSError:
        return 0

def get_stat(filename):
    try:
        return stat(filename)
    except OSError:
        print ("Error: utls.get_stat")
        return (0,) * 10

def getenv(var):
    """Get a value from environment variables"""
    if var in sdata.sysconfig["env"]:
        return sdata.sysconfig["env"][var]
    else:
        return""
    #for k, v in sdata.sysconfig["env"].items():
    #    if k == var:
    #        return v
    #return("")

def setenv(var, val):
    """Set a value to a environment variable"""
    if var=="" or val == "": return        
    sdata.sysconfig["env"][var]=val
    
def unset(var):
    """Remove a environment variable"""
    if var in sdata.sysconfig["env"]:
        del sdata.sysconfig["env"][var]

def date2s(tms):
    localt = utime.gmtime(tms)
    return f"{localt[2]:0>2}/{localt[1]}/{localt[0]:0>4}"

def time2s(tms):
    localt = utime.gmtime(tms)
    return f"{localt[3]:0>2}:{localt[4]:0>2}:{localt[5]:0>2}"

#def timed_function(f, *args, **kwargs):
#    fname = str(f).split(' ')[1]
#    def new_func(*args, **kwargs):
#        t = utime.ticks_us()
#        result = f(*args, **kwargs)
#        delta = utime.ticks_diff(utime.ticks_us(), t)
#        print(f"Function {fname} {args[1]} Time = {delta/1000:6.3f}ms")
#        return result
#    return new_func

# ---

#def dump(obj, file):
#    jdump(obj, file)
    
#def load(file):
#    return jload(file)

def save_conf_file(obj, path):
    with open(path, "w") as cf:
        jdump(obj, cf)

def load_conf_file(path):
    with open(path, "r") as cf:
        return jload(cf)

# ---

def protected(path):
    
    if not "/" in path:
        if getcwd() == "/":
            path = "/" + path
        else:
            path = getcwd() + "/" + path
        
    #print(sdata.sysconfig["pfiles"])
    #print(path)
    
    if path in sdata.sysconfig["pfiles"]:
        return True
    else:
        return False

def human(bytes):
    if bytes > 1024:
        if bytes > 1024 * 1024:
            return f"{bytes / (1024 * 1024):7.2f}M"
        else:
            return f"{bytes / 1024:7.2f}K"
    return f"{bytes:7} "

def tspaces(t, n=12, ab="a", fc=" "):
    """Fill a text(t) with a number (n) of spaces after or before (ab) with a fill character (fc)"""
    tl=len(t)
    f=n-tl
    if f < 2: return t
    if ab == "a":
        t = t + (fc*f)
    else:
        t = (fc*f) + t
    return t

def mac2Str(mac): # b'`U\xf9~x\xd0'
    return ':'.join([f"{b:02X}" for b in mac])

def getgpio(pin):
    """Get the gpio assigned to a pin"""
    gpios=sdata.board["gpio"][0]
    for k, v in gpios.items():
        if v == pin:
            return int(k)
    return 0

def getgpios(cat, ins):
    """Get a dict of pins for a specific service category and controller"""
    gps={}
    gpios=sdata.board["gpio"][0]
    #print(gpios)
    for kps, vps in sdata.board[cat][ins].items():
        for k, v in gpios.items():
            #print(type(k), type(v))
            if v == vps:
                gps[kps]=int(k)
                #print(kps, k)
    return gps

def shlex(ent):
    """cmd line sh lexical parser"""
    args = []
    argact = ""
    incom = False

    for c in ent:
        if c == '"':
            incom = not incom
        elif c == ' ' and not incom:
            if argact:
                args.append(argact)
            argact = ""
        else:
            argact += c

    if argact:
        args.append(argact)

    return args

# Recovery mode:
#import utls
#utls.recovery()
def recovery():
    import kernel
    upyos = kernel.upyOS("-r") # Boot_args: -r

#if __name__ == "__main__":      
#    print(human(1257))
#    print(tspaces("rafa", 12, "b", " "))

#    gpios = getgpio("i2c", 0)
#    gpios = getgpios("i2c", 0)
#    print(gpios)
#    print(getgpio(4))
#    setenv("$?", 10)
#    print(getenv("$?"))
