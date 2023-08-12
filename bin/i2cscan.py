import machine
import sdata
import utls

#print(sdata.board["i2c"])
#TODO: Get gpios from board pins
#scl1=sdata.board["i2c"][0]["scl"]
#sda1=sdata.board["i2c"][0]["sda"]

#TODO: check
gpios = sdata.getgpio("i2c", 0)
print(gpios)

#TODO: check, get string???
scl1=gpios["scl"]
sda1=gpios["sda"]

print(scl1)
print(sda1)

i2c = machine.I2C(scl=machine.Pin(scl1), sda=machine.Pin(sda1))

print('Scan i2c bus...')
devices = i2c.scan()

if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:',len(devices))

  for device in devices:  
    print("Decimal address: ",device," | Hexa address: ",hex(device))
