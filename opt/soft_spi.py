from machine import Pin, SoftSPI
import ssd1306
import time
import network
import dht
import utls

proc=None

def __main__(args):

    #Display
    spi = SoftSPI(baudrate=500000, polarity=1, phase=0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))

    dc = Pin(6)    # data/command
    rst = Pin(11)  # reset
    cs = Pin(7)    # chip select, some modules do not have a pin for this

    display = ssd1306.SSD1306_SPI(128, 64, spi, dc, rst, cs)

    # Temp
    pin=utls.getgpio(29)
    #print(pin)
    sensor = dht.DHT11(Pin(pin))

    while True:
        try:
        
            if proc and proc.sts == "S": break # If thread, stop instruction
            
            if proc.sts=="H":
                utime.sleep(5)
                continue

            sta_if = network.WLAN(network.STA_IF)
            ip = sta_if.ifconfig()[0]

            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
            #temp_f = temp * (9/5) + 32.0
            #print('\nTemperature: %3.1f C' %temp)
            #print('Temperature: %3.1f F' %temp_f)
            #print('Humidity: %3.1f %%' %hum)

            # Limpiar la pantalla
            display.fill(0)
            display.show()

            # Dibujar texto
            display.text('Hola ESP32-C3!', 0, 0, 1)
            display.text('MicroPython', 0, 16, 1)
            display.text('SSD1306 SPI', 0, 26, 1)
            display.show()

            #print(ip)
            display.text(ip, 0, 36, 1)
            display.show()

            # Mostrar temp/hum
            t='T:%3.1f C' % temp
            h='H:%3.1f %%' % hum
            display.text(t + "/" + h , 0, 46, 1)
            display.show()

            # Dibujar una línea
            display.line(0, 56, 127, 56, 1)
            display.show()
            time.sleep(5)
           
        except OSError as e:
            print('Failed to read sensor.'+ str(e))
    






