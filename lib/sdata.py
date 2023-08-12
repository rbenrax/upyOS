# Global system data module

name    = ""
version = ""
debug   = True

board={}
sysconfig={}

# ---

#board={"i2c"   : [{"scl": 27, "sda": 28}],
#       "gpio"  : [{0: 2, 1: 3, 2: 19, 3: 20, 4: 28, 5: 27, 6: 22, 7: 23, 8: 29, 9: 30, 10: 21, 11: 24, 12: 04, 13: 10, 18: 5, 19: 6 }]}
#TODO: check
def getgpio(cat, ins):
    gps={}
    gpios=board["gpio"][0]
    for kps, vps in board[cat][ins].items():
        for k, v in gpios.items():
            if v == vps:
                gps[kps]=k
    return gps

if __name__ == "__main__":
    
    gpios = getgpio("i2c", 0)
    print(gpios)