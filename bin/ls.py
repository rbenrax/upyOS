import uos
import utime
from utls import MONTH
import sdata

def human(bytes):
    """Format bytes in human-readable format"""
    if bytes > 1024:
        if bytes > 1024 * 1024:
            return f"{bytes / (1024 * 1024):7.2f}M"
        else:
            return f"{bytes / 1024:7.2f}K"
    return f"{bytes:7} "

def info(path="", mode="-l"):
    
    # Get filename from path
    filename = path.split("/")[-1]
    
    # Hidden files
    if not "a" in mode:
        if filename[0] == ".": 
            return 0
    
    # Call stat() only once and cache the result
    try:
        stat = uos.stat(path)
    except OSError:
        print("File not found")
        return 0
    
    # Extract stat fields
    stat_mode = stat[0]
    size = stat[6]
    mtime = stat[8]
    localtime = utime.localtime(mtime)

    # Check if directory using stat mode bits directly
    is_dir = (stat_mode & 0x4000) != 0
    
    if is_dir:
        fattr = "d"
        if size > 1000000: 
            size = 0  # TODO: Correct huge size in dirs
    else:
        fattr = " "

    # Check if protected (inline for performance)
    if "/" not in path:
        abs_path = ("/" + path) if uos.getcwd() == "/" else (uos.getcwd() + "/" + path)
    else:
        abs_path = path
    
    if abs_path in sdata.sysconfig["pfiles"]:
        fattr += "r-"
    else:
        fattr += "rw"

    # Check if executable
    if ".py" in path or ".sh" in path:
        fattr += 'x'
    else:
        fattr += '-'
    
    # Format size
    if "h" in mode:
        ssize = human(size)
    else:
        ssize = f"{size:7}"
        
    # Print file info
    if not "n" in mode:
        if "d" in mode:  # Extended date format
            print(f"{fattr} {ssize} {localtime[0]:>4} {localtime[1]:0>2} {localtime[2]:0>2} " + \
                  f"{localtime[3]:0>2}:{localtime[4]:0>2}:{localtime[5]:0>2} {filename}")
        else:
            print(f"{fattr} {ssize} {MONTH[localtime[1]]} {localtime[2]:0>2} " + \
                  f"{localtime[3]:0>2}:{localtime[4]:0>2}:{localtime[5]:0>2} {filename}")
          
    return (size, is_dir)  # Return both size and directory flag for reuse


def ls(path="", mode="-l"):

    cur_dir = uos.getcwd()
    tsize = 0
    
    # Check if path is directory using direct stat
    try:
        path_stat = uos.stat(path) if path else uos.stat(".")
        if not (path_stat[0] & 0x4000):
            print("Invalid directory")
            return tsize
    except OSError:
        print("Invalid directory")
        return tsize
    
    uos.chdir(path)
    
    if path == "" or path == "..": 
        path = uos.getcwd()
    
    if len(path) > 0:
        if path[0] != "/": 
            path = "/" + path
        if path[-1] != "/": 
            path += "/"
    
    tmp = uos.listdir()
    tmp.sort()
    
    for file in tmp:
        fullpath = path + file
        size, is_dir = info(fullpath, mode)  # Get both size and directory flag
        tsize += size
        
        # For recursive mode, use cached is_dir flag (no duplicate stat!)
        if "s" in mode and is_dir:
            print("\n" + fullpath + ":")
            tsize += ls(fullpath, mode)
            print("")
    
    uos.chdir(cur_dir)
    
    if not 'k' in mode:
        if 'h' in mode:
            print(f"\nTotal {path}: {human(tsize)}")
        else:
            print(f"\nTotal {path}: {tsize} bytes")

    return tsize

def __main__(args):

    path=""
    mod="-l"

    if "--h" in args:
        print("List files and directories, ls <path> <options>, --h -lhasnkd")
        print("-h: human readable, -a: incl. hidden, -s: subdirectories, -k: no totals, -n: no file details, -d: full date")
        return

    if len(args)==1:
        if "-" in args[0]:
            mod=args[0]
        else:
            path=args[0]
            
    elif len(args)>1:
        if "-" in args[0]:
            mod = args[0]
            path = args[1]
        else:
            mod = args[1]
            path = args[0]
        
    ls(path, mod)


