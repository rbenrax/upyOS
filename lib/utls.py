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

# ---

import sysdata
if __name__ == "__main__":      
    b=sysdata.SysData("ESP32C3 module with ESP32C3")

    print(b.getBoard())

    s=dumps(b.getBoard())
    print(s)

    o = loads(s)
    b.setBoard(o)
    
    print(b.getBoard())
    
    with open("board.board", "w") as f:
        s=dump(b.getBoard(), f)
        print(s)
        
    with open("board.board", "e") as f:
        o=load(f)
        b.setBoard(o)
        
        print(b.getBoard())
        
    
