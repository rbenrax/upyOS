# Complete project details at https://RandomNerdTutorials.com

import dht
from machine import Pin
from time import sleep

from utls import getgpio

proc=None

def __main__(args):

    sensor = dht.DHT11(Pin(getgpio(19)))

    while True:
      try:
        
        if proc.sts=="S":break
        
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
