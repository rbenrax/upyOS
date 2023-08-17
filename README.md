# smolOS

smolOS - a tiny and simple operating system for MicroPython (targetting ESP8266, RP2040, ESP32-C3, ETC.) giving the user POSIX-like environment to play by Krzysztof Krystian Jankowski.

[smolOS original github site](https://github.com/w84death/smolOS/tree/main)

[smolos docs site](http://smol.p1x.in/os/)


This is a simple test implementation with some modifications of smolOS over ESP32-C3/YD-RP2040 by rbenrax.

The target is to get a common base to use stand alone microcontroller, and fun using it. 

Luatos esp32-c3
![luatos](media/luatos_CORE-ESP32_pinout.webp)

VCC-GND Studio YD-2040
![VCC-GND Studio](media/YD-2040-PIN.png)
![luatos on esp32-c3](media/smolos_01.png )

Actual Development:

- /lib/grubs.py the first process in boot, will create .board file in /etc directory if does not exists, this file shoud be edited to acomodate all the board resources available, if the .board file exists, smolos process will read its content and will enable the resources to be used by the system, modules, external commands, etc.

- /lib/smolos.py is the next load, is the OS core, has internal and external commands (/bin directory), all commands will be moved to external commands to reduce the memory use.

- Actual implementation also can call simple shell scripts, including /etc/rc.local, the start up script, every script can share argument stored in sdata.sysconfig[env] dictionary.

- Added editor from https://github.com/octopusengine/micropython-shell/tree/master

. Reduced memory usage to fit on esp8266

- Added recovery mode, to avoid load of start up failed commands

- Directories:
-   bin: External caommads (.py, .sh)
-   lib: smolOS implementation
-   extlib: External libraries directory
-   etc: Configuation files
-   opt: Externa python programs (ex. specific applications)
-   tmp: temporal firectory

TODO List:
- Enhance and move external ls, cp, mv, etc. commands
- Add regexp and directories to file managements
- Add grep, du, diff, find, tar, uname and hostname.
- Revise protected files and directories
- Enhance help
- 

Wishlist is open ;)

