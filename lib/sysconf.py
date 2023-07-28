import json

class Sysconf():
    def __init__(self, board):
        
        self.sysconf={"ver"    : 1.0,
                      "aliases"  : {"name": board, "manufacturer": "vcc-gnd studio"},
                      "rofiles"    : {"type": "esp32-c3", "arch": "risc-v", "speed": "80,160"},
                      "eth"    : False,
                      "wifi"   : True,
                      "bt"     : True,
                      "ir"     : False,
                      "rtc"    : False,
                      "temp"   : False
                    
                    }


    def getSysconf(self):
        return self.sysconf
    
    def dumps(self):
        return json.dumps(self.sysconf)
    
    def loads(self, data):
         self.sysconf = json.loads(data)
         
if __name__ == "__main__":      
    b=BoardDef("sysconf")

    print("Original")
    print(b.getSysconf())

    s=b.dumps()
    print("Codificada")
    print(s)

    b.loads(s)
    print("cargada")
    print(b.getSysconf())
