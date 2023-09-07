# Global system data module

name    = ""
version = ""
debug   = True

board={}
sysconfig={}

# ---

#To local check
#board={"i2c"   : [{"scl": 27, "sda": 28}],
#       "gpio"  : [{"0": 2, "1": 3, "2": 19, "3": 20, "4": 28, "5": 27, "6": 22, "7": 23, "8": 29, "9": 30, "10": 21, "11": 24, "12": 04, "13": 10, "18": 5, "19": 6 }]}

#sysconfig ={"env" : {"$?": "9", "$0": "a", "$1": "b", "$2": "c", "$3": "d"}}

def getenv(var):
    """Get a value from environment variables"""
    #print(sysconfig["env"])
    for k, v in sysconfig["env"].items():
        if k == str(var):
            return v
    return("")

def setenv(var, val):
    """Set a value to a environment variable"""
    sysconfig["env"][str(var)]=str(val)

def unset(var):
    """Remove a environment variable"""
    if sysconfig["env"][str(var)]:
        del sysconfig["env"][str(var)]

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
    gpios=board["gpio"][0]
    #print(gpios)
    for kps, vps in board[cat][ins].items():
        for k, v in gpios.items():
            #print(type(k), type(v))
            if v == vps:
                gps[kps]=int(k)
                #print(kps, k)
    return gps

#if __name__ == "__main__":
    
    #gpios = getgpios("i2c", 0)
    #print(gpios)
    #print(getgpio(4))
    #setenv("$?", 10)
    #print(getenv("$?"))
