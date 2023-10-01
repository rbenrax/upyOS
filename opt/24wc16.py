
# Read/write I2C bus 24wc16 memory 

from time import sleep
from machine import I2C, Pin
import utls

def __main__(args):
    
    i2c_id=0
    gpios = utls.getgpios("i2c", i2c_id)
    print(gpios)

    i2c = I2C(id=i2c_id, scl=Pin(gpios["scl"]), sda=Pin(gpios["sda"]), freq=400000)

    devs=i2c.scan()
    for device in devs:  
        print("Address: h", hex(device), ' b', bin(device))

    #i2c.writeto_mem(0x50, 0, bytearray('Hola Rafa'))
    #sleep(0.01)

    #for i in range(16):
    #    i2c.writeto_mem(0x50, i, b'\xff')
    #    

    #for device in devs:
    #   i2c.writeto_mem(device, 0, b'\xff')
    #    sleep(0.01)

    print(devs[2:])

    #f=open('mem.bin', 'w')
    ga=0 # global address
    for chip in devs[2:]:

      for addr in range(256):

        if (ga%16==0):
            print('\n', end = ' ')
            print(hex(ga) + '\t', end = ' ')
            
        v = i2c.readfrom_mem(chip, addr, 1)
        #f.write(v)
        i = int.from_bytes(v, "big")
        #s=str(v)[2:-1]
        
        if i>32 and i< 127:
            print(chr(i), end = ' ')
        else:
            print('.', end = ' ')
            
        ga+=1
        
    #f.close()

if __name__ == "__main__":
    args =[""]
    __main__(args)
    
