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

NodeMCU
![NodeMCU esp8266](media/Node-MCU-Pinout.png )

![luatos on esp32-c3](media/smolos_01.png )


MPY: soft reboot


Booting smolOS...
Board config loaded.
System config loaded.
CPU speed set to 160 Mhz

->Normal mode boot
                                 ______  _____     
           _________ ___  ____  / / __ \/ ___/     
          / ___/ __ `__ \/ __ \/ / / / /\__ \      
         (__  ) / / / / / /_/ / / /_/ /___/ /      
        /____/_/ /_/ /_/\____/_/\____//____/       
-------------TINY-OS-FOR-TINY-COMPUTERS------------

Board: Arduino Nano RP2040 Connect with RP2040
MicroPython: 1.20.0
smolOS-rp2 : 0.5 rbenrax (size: 11730 bytes)
Firmware:v1.20.0 on 2023-04-26 (GNU 12.1.0 MinSizeRel)
CPU Speed:160.0MHz In power-saving, slow mode. Use `cpuclock` command to set speed.
Memory:
Total.:  204416 bytes
Alloc.:   26528 bytes
Free..:  177888 bytes (87.02%)
Storage:
Total space:  8364032 bytes
Used space.:   286720 bytes
Free space.:  8077312 bytes
Launching rc.local:

->Type 'help' for a smol manual.

/ $: help
smolOS-rp2 version 0.5 rbenrax

smolOS Help:

Adapted by rbenrax, source available in https://github.com/rbenrax/smolOS 
Based in Krzysztof Krystian Jankowski work available in smol.p1x.in/os/

Explanation:

The objective is to provide one more layer to micropython that allows us to manage a microcontroller in a similar way to what we use every day in a common computer, with the use of simpler programs that can be complemented in a more flexible way.

In main.py we can launch grub or smolos directly (see files).

Grub will create in /etc dir a file (if doesn't exists) for configure the specific board pins, gpios and other parameters, also allow stop the system boot if any program hung the load.

In smolos boot two shell scripts ar executed, init.sh and rc.local, init.sh will launch system start up commands, and rc.local programa and commands specifics for a user solution.

Exists internal and external commands, and internal and externals shell scripts, internal located in /bin directory and are exceuted without extention, external can be located in any directory and are executed thin 'run' and 'sh' commands with file extention, external commands are self-explanatory and some have help (--h).

The system can be extended with more external commands and programs with the aim of keeping the memory footprint as low as possible, because the ram is quite small but the flash is big enough.

The sdata module contains all the system data, allowing access to the board configuration parameters, system configuration parameters, etc., allowing access to these parameters between programs.

If system hungs in boot (ex. defective program), we can delete init.sh, then the system wil boot in recovery mode, also we canuse recovery command in any time, which moves init.sh to init.rec and viceversa.

I hope it is useful for you!, there are things to do, and improve, but the holidays are running out.

Directories structure:

/
boot.py         Micropython statup file
main.py         Micropython statup file (boot system)

    /bin        Commands and shell scripts
    /ext        Configuration files
    /extlib     External libraries
    /lib        System implementations libraries
    /opt        Specific solution or add-on programs
    /tmp        Temporary directory (to put what you don't know where to put :-)


Internals commands:

help:   This help
ls:     List files and directories
cat:    print files content
cp:     Copy files
mv:     Move files
rm:     Remove files
clear:  Clears the screen
info:   Get information about a file
run:    runs external python program
sh:     run external sh script
py:     Run python code
pwd:    Show current directory
mkdir:  Make directory
rmdir:  Remove directory
cd:     Change default directory
exit:   Exit to Micropython shell

External commands:

cpuclock, df, free, i2cscan, ifconfig, led, lineup, lshw, lsmod, mem_info, modules, ping, reboot, recovery, rmmod, sh.sh, test, touch, uhttpd, uptime, utelnetd, vi, wait, wget, wifi




Actual Development:

- /lib/grubs.py the first process in boot, will create .board file in /etc directory if does not exists, this file shoud be edited to acomodate all the board resources available, if the .board file exists, smolos process will read its content and will enable the resources to be used by the system, modules, external commands, etc.

- /lib/smolos.py is the next load, is the OS core, has internal and external commands (/bin directory), all commands will be moved to external commands to reduce the memory use.

- Actual implementation also can call simple shell scripts, including /etc/rc.local, the start up script, every script can share argument stored in sdata.sysconfig[env] dictionary.

- Added editor from https://github.com/octopusengine/micropython-shell/tree/master

- Reduced memory usage to fit on esp8266

- Added recovery mode, to avoid load of start up failed commands

TODO List:
- Enhance and move to external ls, cp, mv, etc. commands
- Add regexp and directories to file managements
- Add grep, du, diff, find, tar, uname and hostname.
- Revise protected files and directories
- Enhance help
- 

Wishlist is open ;)

