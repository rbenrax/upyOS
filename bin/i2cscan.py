import machine
import utls
import sdata

#print(utls.board["i2c"])
#scl1=utls.board["i2c"][0]["scl"]
#sda1=utls.board["i2c"][0]["sda"]

def __main__(args):

    if len(args) == 0:
        print("Scan i2c bus for devices\nUsage: i2cscan <bus>: 0,1,..")
        return
    else:
        buses=len(sdata.board["i2c"])
        if buses>0:
            i2c_id=int(args[0])
            if i2c_id <= buses-1:
                gpios = utls.getgpios("i2c", i2c_id)
                print(gpios)

                i2c = machine.I2C(id=i2c_id, scl=machine.Pin(gpios["scl"]), sda=machine.Pin(gpios["sda"]))

                print('Scan i2c bus...')
                devices = i2c.scan()

                if len(devices) == 0:
                    print("No i2c device !")
                else:
                    print('i2c devices found:',len(devices))

                    for device in devices:  
                        print("Decimal address: ", device, " | Hexa address: ", hex(device))
            else:
                print(f"I2C bus {i2c_id} not exists in this board")
        else:
            print("This board seems has no I2C bus")
