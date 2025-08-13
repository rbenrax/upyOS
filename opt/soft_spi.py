from machine import Pin, SoftSPI
import ssd1306
import time
import network
import dht
import utls

proc=None

#ESP32-C3  ->  Display SSD1306
#-----------------------------
#GND       ->  GND
#3.3V      ->  VCC
#GPIO6     ->  SCK  D0
#GPIO7     ->  MOSI D1
#GPIO2     ->  MISO (unused)
#GPIO11    ->  RES (Reset)
#GPIO3     ->  DC (Data/Command)
#GPIO10    ->  CS (Chip Select)

def __main__(args):

    #Display
#     sspi = SoftSPI(baudrate=500000, polarity=1, phase=0, sck=Pin(6), mosi=Pin(7), miso=Pin(2))

#     rst = Pin(11)   # reset
#     dc  = Pin(3)    # data/command
#     cs  = Pin(10)   # chip select, some modules do not have a pin for this

#     display = ssd1306.SSD1306_SPI(128, 64, sspi, dc, rst, cs)

    import sdata
    display = sdata.d0

    # Temp
    pin=utls.getgpio(29)
    #print(pin)
    sensor = dht.DHT11(Pin(pin))

    while True:
        try:
        
            if proc and proc.sts == "S":
                display.fill(0)
                display.text("Finalizado", 0, 0, 1)
                display.show()
                break # If thread, stop instruction
            
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
            display.text('SSD1306 SPI SW', 0, 26, 1)
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
    






