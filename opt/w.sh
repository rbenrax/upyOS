# Shell script 
#loadboard /etc/upyOS-esp32c3_vcc_gnd.board

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

# Display0 driver load
> from machine import Pin, SPI
> import ssd1306
> sdata.d0 = ssd1306.SSD1306_SPI(128, 64, SPI(1), Pin(3), Pin(11), Pin(10))
> d0 = sdata.d0

> d0.fill(0)
> d0.text(sdata.name, 0, 0, 1)
> d0.text("Iniciando...", 0, 16, 1)
> d0.show()

# Wifi sta
wifi sta on                      # Turn on wifi in cliente mode

#wifi sta status   
#wifi sta scan                   # scan wifi APs

# Crear variable de entorno
export essid xxxxxxxx
export passw xxxxxxxx

> d0.text("Try.. " + utls.getenv("essid"), 0, 26, 1)
> d0.show()

#wifi sta connect xxxxx xxxxx 10 # Connect to wifi router

wifi sta connect $essid $passw 10 # Connect to wifi router

wifi sta status -n
if $0 == 0 goto exit
if $1 == 0 goto exit

> d0.text("Conected", 0, 36, 1)
> d0.show()

ntpupdate es.pool.ntp.org
date

> d0.text("ntpupdate", 0, 46, 1)
> d0.text("Ready", 0, 56, 1)
> d0.show()

wifi sta ifconfig

utelnetd start
uftpd start

# uhttpd start &
#/opt/asy_test &

# /opt/dht11_2.py &
/opt/hard_spi.py &

:exit
unset essid
unset passw
