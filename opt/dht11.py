# Complete project details at https://RandomNerdTutorials.com

from machine import Pin
from time import sleep
import dht
import utime

proc=None

def __main__(args):

    import utls
    pin=utls.getgpio(19)

    sensor = dht.DHT11(Pin(pin))

    while True:
        try:
        
            if proc and proc.sts == "S": break # If thread, stop instruction
            
            if proc.sts=="H":
                utime.sleep(1)
                continue

            sleep(2)
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
            #temp_f = temp * (9/5) + 32.0
            print('\nTemperature: %3.1f C' %temp)
            #print('Temperature: %3.1f F' %temp_f)
            print('Humidity: %3.1f %%' %hum)
            
        except OSError as e:
            print('Failed to read sensor.'+ str(e))
    
    