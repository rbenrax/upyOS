# smolOS

smolOS - a tiny and simple operating system for MicroPython (targetting ESP8266, RP2040, ESP32-C3, ETC.) giving the user POSIX-like environment to play by Krzysztof Krystian Jankowski.

[smolOS original github site](https://github.com/w84death/smolOS/tree/main)

[smolos docs site](http://smol.p1x.in/os/)


This is a simple test implementation with some modifications of smolOS over ESP32-C3/YD-RP2040 by rbenrax.

Luatos esp32-c3
![luatos](media/luatos_CORE-ESP32_pinout.webp)

VCC-GND Studio YD-2040
![VCC-GND Studio](media/YD-2040-PIN.png)
![luatos on esp32-c3](media/smolos_01.png )

TODO List:
- Create .board file in grub.py in directory /etc, read in boot
- Add board caracteristics, including digital pins, ADC pins, PWM pins, i2c pins and SPI pins, etc, and losting in lshw
- Enhance ls command
- Editor to external .py
- Add regexp and directories to file managements
- Add Wifi client and AP
- Add grep, du, diff, find, tar, ping, ip, uname, hostname and wget.
-

Wishlist is open ;)
