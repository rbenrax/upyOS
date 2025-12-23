# Utility functions

import utime
from uos import stat
from uos import getcwd
from json import dump as jdump
from json import load as jload

import sdata

MONTH = ('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
WEEKDAY = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')

# -- Cache control
# Cached stat results to avoid repeated filesystem calls
_stat_cache = {}
_cache_timeout = 1000  # 1 second cache timeout

def _get_cached_stat(filename):
    """Get file stat with caching to reduce filesystem calls"""
    current_time = utime.ticks_ms()
    
    # Check if cache is enabled and has valid entry
    if sdata.cache_enabled and filename in _stat_cache:
        cached_stat, timestamp = _stat_cache[filename]
        if utime.ticks_diff(current_time, timestamp) < _cache_timeout:
            return cached_stat
    
    try:
        file_stat = stat(filename)
        # Only cache if enabled
        if sdata.cache_enabled:
            _stat_cache[filename] = (file_stat, current_time)
        return file_stat
    except OSError:
        # Cache negative results too, but only if enabled
        if sdata.cache_enabled:
            _stat_cache[filename] = (None, current_time)
        return None

def file_exists(filename):
    """Check if file exists using cached stat"""
    #file_stat = _get_cached_stat(filename)
    #return file_stat is not None and (file_stat[0] & 0xc000) != 0

    try:
        stat(filename)
        return True
    except OSError:
        return False

def isdir(filename):
    """Check if path is directory using cached stat"""
    file_stat = _get_cached_stat(filename)
    return file_stat is not None and (file_stat[0] & 0x4000) != 0

def isfile(filename):
    """Check if path is file using cached stat"""
    file_stat = _get_cached_stat(filename)
    return file_stat is not None and (file_stat[0] & 0x8000) != 0

def get_mode(filename):
    """Get file mode using cached stat"""
    file_stat = _get_cached_stat(filename)
    return file_stat[0] if file_stat else 0

def get_stat(filename):
    """Get full file stat with error handling"""
    file_stat = _get_cached_stat(filename)
    if file_stat is None:
        print("Error: utls.get_stat")
        return (0,) * 10
    return file_stat

# -- Env var

def getenv(var):
    """Get a value from environment variables"""
    if var in sdata.sysconfig["env"]:
        return sdata.sysconfig["env"][var]
    else:
        return ""

def setenv(var, val):
    """Set a value to an environment variable"""
    if var=="": return        
    sdata.sysconfig["env"][var]=val
    
def unset(var):
    """Remove an environment variable"""
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
    incom_doble = False
    incom_simple = False
    escape = False
    quote_stack = []  # Stack to handle nested quotes

    for c in ent:
        if escape:
            # If we are in escape mode, add the character literally
            argact += c
            escape = False
        elif c == '\\':
            # Start escape sequence
            escape = True
        elif c == '"' and not incom_simple and not escape:
            if incom_doble:
                # Closing double quote
                incom_doble = False
                if quote_stack and quote_stack[-1] == '"':
                    quote_stack.pop()
            else:
                # Opening double quote
                incom_doble = True
                quote_stack.append('"')
        elif c == "'" and not incom_doble and not escape:
            if incom_simple:
                # Closing single quote
                incom_simple = False
                if quote_stack and quote_stack[-1] == "'":
                    quote_stack.pop()
            else:
                # Opening single quote
                incom_simple = True
                quote_stack.append("'")
        elif c == ' ' and not incom_doble and not incom_simple:
            if argact:
                args.append(argact)
                argact = ""
        else:
            argact += c

    if argact:
        args.append(argact)

    return args

def sha1(data, is_file=False):
    """Generate SHA1 hash of a string or file"""
    if not data:
        return ""
    
    import uhashlib
    import ubinascii
    h = uhashlib.sha1()
    if is_file:
        with open(data, 'rb') as f:
            while True:
                chunk = f.read(512)
                if not chunk:
                    break
                h.update(chunk)
    else:
        h.update(data.encode())
    return ubinascii.hexlify(h.digest()).decode()

def log(src, msg):
    if sdata.log:
        print(f"{src}: {msg}")

# Recovery mode:
#import utls
#utls.recovery()
def recovery():
    import kernel
    upyos = kernel.upyOS("-r") # Boot_args: -r

# Redirect output to an env var or file or print in terminal
def outs(args, val, prt=True):
    if ">>" not in args and ">" not in args:
        if prt:
            print(val)
        return False

    try:
        # Detect operator and open mode
        if ">>" in args:
            idx, mode = args.index(">>"), "a"
        else:
            idx, mode = args.index(">"), "w"

        # Validar destino
        if idx + 1 >= len(args):
            print("Error: missing destination after '>'")
            return False

        target = args[idx + 1]
        
        # Redirect to file
        if "." in target or "/" in target:
            with open(target, mode) as f:
                f.write(str(val) + "\n")
        else:
            # Redirect to "environment variable"
            if mode == "a":
                current = getenv(target)
                setenv(target, current + val)
            else:
                setenv(target, val)

        return True

    except Exception as e:
        print(f"Error outs: {e}")
        return False

#def strip_quot(v):
#    return v[1:-1] if len(v) >= 2 and v[0] in ('"', "'") and v[-1] == v[0] else v


#if __name__ == "__main__":      
#    print(human(1257))
#    print(tspaces("rafa", 12, "b", " "))

#    gpios = getgpio("i2c", 0)
#    gpios = getgpios("i2c", 0)
#    print(gpios)
#    print(getgpio(4))
#    setenv("$?", 10)
#    print(getenv("$?"))