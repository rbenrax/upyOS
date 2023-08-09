# file utls
import os
import json

MONTH = ('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
WEEKDAY = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')

def file_exists(filename):
    return get_mode(filename) & 0xc000 != 0

def isdir(filename):
    return get_mode(filename) & 0x4000 != 0

def isfile(filename):
    return get_mode(filename) & 0x8000 != 0

def get_mode(filename):
    try:
        return os.stat(filename)[0]
    except OSError:
        return 0

def get_stat(filename):
    try:
        return os.stat(filename)
    except OSError:
        return (0,) * 10

# ---

def dump(obj, file):
    json.dump(obj, file)
    
def load(file):
    return json.load(file)

def dumps(obj):
    return json.dumps(obj)
    
def loads(data):
    return json.loads(data)

def load_conf_file(path):
    with open(path, "r") as cf:
        return load(cf)

def save_conf_file(obj, path):
    with open(path, "w") as cf:
        dump(obj, cf)

# ---

def human(bytes):
    if bytes > 1024:
        if bytes > 1024 * 1024:
            return f"{bytes / (1024 * 1024):7.2f}MB"
        else:
            return f"{bytes / 1024:7.2f}KB"
    return f"{bytes:7}B"

# ---


if __name__ == "__main__":      
    print(human(1257))
        
    
