# file utls
import sdata

from uos import stat
from uos import getcwd

from json import dump as jdump
from json import load as jload

MONTH = ('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
#WEEKDAY = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')

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
        return (0,) * 10

# ---

def dump(obj, file):
    jdump(obj, file)
    
def load(file):
    return jload(file)


def load_conf_file(path):
    with open(path, "r") as cf:
        return load(cf)

def save_conf_file(obj, path):
    with open(path, "w") as cf:
        dump(obj, cf)

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

#To local check
#board={"i2c"   : [{"scl": 27, "sda": 28}],
#       "gpio"  : [{"0": 2, "1": 3, "2": 19, "3": 20, "4": 28, "5": 27, "6": 22, "7": 23, "8": 29, "9": 30, "10": 21, "11": 24, "12": 04, "13": 10, "18": 5, "19": 6 }]}

#sysconfig ={"env" : {"$?": "9", "$0": "a", "$1": "b", "$2": "c", "$3": "d"}}

def getgpio(pin):
    """Get the gpio assigned to a pin"""
    gpios=board["gpio"][0]
    for k, v in gpios.items():
        if v == pin:
            return int(k)
    return 0

def getgpios(cat, ins):
    """Get a dict of pins for a specific service category"""
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

# - - - -

#if __name__ == "__main__":      
#    print(human(1257))
#    print(tspaces("rafa", 12, "b", " "))

#    gpios = getgpio("i2c", 0)
#    gpios = getgpios("i2c", 0)
#    print(gpios)
#    print(getgpio(4))
#    setenv("$?", 10)
#    print(getenv("$?"))
