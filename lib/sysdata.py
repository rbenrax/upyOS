class SysData():
    def __init__(self, board):
        
        self.board={"ver"   : 1.0,
                    "board" : {"name": board, "vendor": "vcc-gnd studio"},
                    "mcu"   : {"type": "esp32-c3", "arch": "risc-v", "speed": {"slow": 80, "turbo": 160} },
                    "eth"   : False,
                    "wifi"  : True,
                    "bt"    : True,
                    "ir"    : False,
                    "rtc"   : False,
                    "temp"  : False,
                    "text"  : "Example file autogenerated, must be fulfilled",
                    "5v0"   : [16,31],
                    "3v3"   : [13,18,26],
                    "gnd"   : [1,7,14,17,25,32],
                    "ctrl"  : [{"rst": 12, "PWB": 15, "boot":30}],
                    "adc"   : [{"adc0": 2, "adc1": 3, "adc4": 28}],
                    "dac"   : [{"dac0": 0, "dac1": 0}],
                    "pwm"   : [{"pwm1": 22, "pwm2": 19, "pwm3": 21, "pwm4": 29}],
                    "gpio"  : [{"0": 2, "1": 3, "2": 19, "3": 20, "4": 28, "5": 27, "6": 22, "7": 23, "8": 29,
                                "9": 30, "10": 21, "11": 24, "12": 04, "13": 10, "18": 5, "19": 6 }],
                    "ints"  : [{"int1": 0, "int2": 0}],
                    "i2c"   : [{"scl": 27, "sda": 28}],
                    "spi"   : [{"mosi1": 20, "miso1": 21, "cs1": 23, "ck1": 19}],
                    "usart" : [{"tx0": 2, "rx0": 3}, {"tx1": 9, "rx1": 8}],
                    "i2s"   : [{"clk1": 0, "io1": 0}],
                    "can"   : [{"tx1": 0, "rx1": 0}],
                    "usb"   : [{"D+1": 0, "D-1": 0}],
                    "sdio"  : [{"clk": 0, "cmd": 0, "data0": 0, "data1": 0, "data2": 0, "data3": 0 }],
                    "touch" : [{"t1": 0, "t2": 0}],
                    "other" : [{"vout": 0, "vin": 0, "usrkey": 0, "vref": 0, "flash": 0, "wake": 0, "run": 0, "vbat": 0 }],
                    "nc"    : [11],
                    "resv"  : [],
                    "ledio" : [{"d5": 12, "d6": 13}],
                    "rgbio" : [{"l1": 0}]
                    }

        self.sysconf={"ver"     : 1.0,
                      "aliases" : {"h": "help","list": "ls","show": "cat","remove": "rm","edit": "vi"},
                      "turbo"   : False,
                      "wifi"    : {"mode": "AP", "ESSID": "reduno", "password": "123456"}
                     }
        
    def getBoard(self):
        return self.board
    
    def setBoard(self, board):
        self.board=board
 
    def getSysConf(self):
        return self.sysconf
    
    def setSysConf(self, obj):
        self.sysconf=obj
