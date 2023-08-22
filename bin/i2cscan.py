import machine
import sdata

#print(sdata.board["i2c"])
#scl1=sdata.board["i2c"][0]["scl"]
#sda1=sdata.board["i2c"][0]["sda"]

i2c_id=0
gpios = sdata.getgpios("i2c", i2c_id)
print(gpios)

i2c = machine.I2C(id=i2c_id, scl=machine.Pin(gpios["scl"]), sda=machine.Pin(gpios["sda"]))

print('Scan i2c bus...')
devices = i2c.scan()

if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:',len(devices))

  for device in devices:  
    print("Decimal address: ",device," | Hexa address: ",hex(device))
