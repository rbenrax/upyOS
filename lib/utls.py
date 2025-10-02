# Utility functions

import utime
from uos import stat, getcwd
from json import dump as jdump, load as jload
import sdata

MONTH = ('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
WEEKDAY = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')

# Cache control, avoid repeated filesystem calls
_stat_cache = {}
_cache_timeout = const(1000)  # 1 second cache timeout

def _get_cached_stat(filename):
    """Get file stat with caching to reduce filesystem calls"""
    current_time = utime.ticks_ms()
    
    # Check if cache is enabled and has valid entry
    if sdata.cache_enabled and filename in _stat_cache:
        cached_stat, timestamp = _stat_cache[filename]
        if utime.ticks_diff(current_time, timestamp) < _cache_timeout:
            return cached_stat
    
    try:
        fs = stat(filename)
        # Only cache if enabled
        if sdata.cache_enabled:
            _stat_cache[filename] = (fs, current_time)
        return fs
    except OSError:
        # Cache negative results too, but only if enabled
        if sdata.cache_enabled:
            _stat_cache[filename] = (None, current_time)
        return None

def file_exists(filename):
    """Check if file exists using cached stat"""
    fs = _get_cached_stat(filename)
    return fs is not None and (fs[0] & 0xc000) != 0

def isdir(filename):
    """Check if path is directory using cached stat"""
    fs = _get_cached_stat(filename)
    return fs is not None and (fs[0] & 0x4000) != 0

def isfile(filename):
    """Check if path is file using cached stat"""
    fs = _get_cached_stat(filename)
    return fs is not None and (fs[0] & 0x8000) != 0

def get_mode(filename):
    """Get file mode using cached stat"""
    fs = _get_cached_stat(filename)
    return fs[0] if fs else 0

def get_stat(filename):
    """Get full file stat with error handling"""
    fs = _get_cached_stat(filename)
    if fs is None:
        print("Error: utls.get_stat")
        return (0,) * 10
    return fs

# -- Env var

def getenv(var):
    """Get a value from environment variables"""
    if var in sdata.sysconfig["env"]:
        return sdata.sysconfig["env"][var]
    else:
        return ""

def setenv(var, val):
    """Set a value to a environment variable"""
    if var=="" or val == "": return        
    sdata.sysconfig["env"][var]=val
    
def unset(var):
    """Remove a environment variable"""
    if var in sdata.sysconfig["env"]:
        del sdata.sysconfig["env"][var]

# Date time
def date2s(tms):
    localt = utime.gmtime(tms)
    return f"{localt[2]:0>2}/{localt[1]}/{localt[0]:0>4}"

def time2s(tms, mod):
    localt = utime.gmtime(tms)
    
    if "e" in mod: # Time elapsed
        return f"{localt[7]-1:3}d {localt[3]:0>2}:{localt[4]:0>2}:{localt[5]:0>2}"
    else:       # Time regular
        return f"{localt[3]:0>2}:{localt[4]:0>2}:{localt[5]:0>2}"

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

def log(src, msg):
    if sdata.log:
        print(f"{src}: {msg}")

# Recovery mode:
#import utls
#utls.recovery()
def recovery():
    import kernel
    upyos = kernel.upyOS("-r") # Boot_args: -r

# Redirect output to an env var or file
def redir(args, val):
    if ">>" not in args and ">" not in args:
        return False

    try:
        # Detectar operador y modo de apertura
        if ">>" in args:
            idx, mode = args.index(">>"), "a"
        else:
            idx, mode = args.index(">"), "w"

        # Validar destino
        if idx + 1 >= len(args):
            print("Error: falta destino después de '>'")
            return False

        target = args[idx + 1]
        
        # Redirigir a archivo
        if "." in target or "/" in target:
            with open(target, mode) as f:
                f.write(str(val) + "\n")
        else:
            # Redirigir a "variable de entorno"
            if mode == "a":
                current = getenv(target)
                setenv(target, current + val)
            else:
                setenv(target, val)

        return True

    except Exception as e:
        print(f"Error redir: {e}")
        return False

#if __name__ == "__main__":      
#    print(human(1257))
#    print(tspaces("rafa", 12, "b", " "))

#    gpios = getgpio("i2c", 0)
#    gpios = getgpios("i2c", 0)
#    print(gpios)
#    print(getgpio(4))
#    setenv("$?", 10)
#    print(getenv("$?"))
