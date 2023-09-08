
try:
  import usocket as socket
except:
  import socket

import time

from machine import Pin
import network

import esp
esp.osdebug(None)

import gc
gc.collect()

#--- dht11
import dht

if __name__ == "__main__":
    pin=2
else:
    import utls
    pin=utls.getgpio(19)

sensor = dht.DHT11(Pin(pin))
#sensor = dht.DHT11(Pin(2))

def blink(led):
    led.value(1)
    time.sleep(.3)
    led.value(0)
    time.sleep(.3)

ssid = 'SSID'
password = 'PASSWORD'

station = network.WLAN(network.STA_IF)

station.active(True)

if station.isconnected(): station.disconnect()
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())

# Parpadea para darnos la ip
led = Pin(13, Pin.OUT)

ip=(station.ifconfig()[0]).split('.')[3]
print(ip)

# Primero cuantos digitos,
#for p in range(len(ip)):
#    blink(led)

time.sleep(1)

# Despues los digitos de la ip
for d in range(len(ip)):
    for p in range(int(ip[d])):
        blink(led)
    time.sleep(1)

# Complete project details at https://RandomNerdTutorials.com

def web_page():
  if led.value() == 1:
    gpio_state="ON"
  else:
    gpio_state="OFF"
  
  #--dht11
  sensor.measure()
  temp = sensor.temperature()
  hum = sensor.humidity()
  print('\nTemperature: %3.1f C' %temp)
  print('Humidity: %3.1f %%' %hum)

  html = """<html><head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
  border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
  .button2{background-color: #4286f4;}</style></head><body> <h1>ESP Web Server</h1> 
  <p>GPIO state: <strong>""" + gpio_state + """</strong></p><p><a href="/?led=on"><button class="button">ON</button></a></p>
  <p><a href="/?led=off"><button class="button button2">OFF</button></a></p> <p>Temp/Hum: """ + str(temp) + "/" + str(hum) +  """</p>  </body></html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  conn, addr = s.accept()
  print('Got a connection from %s' % str(addr))

  request = conn.recv(1024)
  request = str(request)
  #print('Content = %s' % request)

  led_on = request.find('/?led=on')
  led_off = request.find('/?led=off')

  if led_on == 6:
    print('LED ON')
    led.value(1)
    #time.sleep(1)
    #led.value(0)
  if led_off == 6:
    print('LED OFF')
    led.value(0)
    
  response = web_page()
  conn.send('HTTP/1.1 200 OK\n')
  conn.send('Content-Type: text/html\n')
  conn.send('Connection: close\n\n')
  conn.sendall(response)
  conn.close()

