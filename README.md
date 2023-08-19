# smolOS

smolOS - a tiny and simple operating system for MicroPython (targetting ESP8266, RP2040, etc.) giving the user POSIX-like environment, originally developed by Krzysztof Krystian Jankowski and adapted by me.

[smolOS original github site](https://github.com/w84death/smolOS/tree/main)

[smolos docs site](http://smol.p1x.in/os/)


This is a simple test implementation with some modifications of smolOS over ESP32-C3, ESP8266 and YD-2040 and any others by rbenrax.

The target is to get a common base to use stand alone microcontroller, and fun using it. 

Luatos esp32-c3
![luatos](media/luatos_CORE-ESP32_pinout.webp)

VCC-GND Studio YD-2040
![VCC-GND Studio](media/YD-2040-PIN.png)

NodeMCU
![NodeMCU esp8266](media/Node-MCU-Pinout.png )

![YD-2040](media/smolos_01.png )
![luatos on esp32-c3](media/smolos_02.png )


smolOS Help:

Adapted by rbenrax, source available in https://github.com/rbenrax/smolOS, based in Krzysztof Krystian Jankowski work available in smol.p1x.in/os/

Explanation:

The objective is to provide one more layer to micropython that allows us to manage a microcontroller in a similar way to what we use every day in a common computer, with the use of simpler programs that can be complemented in a more flexible way, obviously at the cost of lower performance and efficiency, but giving more facilities for those who start using microcontrollers.

In main.py we can launch grub or smolos directly (see files).

Grub will create in /etc dir a file (if doesn't exists) for configure the specific board pins, gpios and other parameters, also allow stop the system boot if any program hung the load.

In smolos boot two shell scripts are executed, init.sh and rc.local, init.sh will launch system start up commands, and rc.local programa and commands specifics for a user solution, you can remove the commands you don't need and make the boot as fast as you want, as well as include commands or programs that you need .

Exists internal and external commands, and internal and externals shell scripts, internal located in /bin directory and are exceuted without extention, external can be located in any directory and are executed thin 'run' and 'sh' commands with file extention, external commands are self-explanatory and some have help (--h).

The system can be extended with more external commands and programs with the aim of keeping the memory footprint as low as possible, because the ram is quite small but the flash is big enough.

The sdata module contains all the system data, allowing access to the board configuration parameters, system configuration parameters, etc., allowing access to these parameters between programs.

Environmet variables can be set, get and unset from commands/scripts (export, echo, unset) and python programs by sdata.getenv() and setenv() functions

If system hungs in boot (ex. defective program), we can delete init.sh, then the system wil boot in recovery mode, also we can use recovery command in any time, which moves init.sh to init.rec and viceversa.

I hope it is useful for you!, there are things to do, and improve, but the holidays are running out.

Directories structure:

- boot.py         Micropython statup file
- main.py         Micropython statup file (boot system)

      /bin        Commands and shell scripts
      /ext        Configuration files
      /extlib     External libraries
      /lib        System implementations libraries
      /opt        Specific solution or add-on programs
      /tmp        Temporary directory (to put what you don't know where to put :-)


Internals commands:

- help:   This help
- ls:     List files and directories
- cat:    print files content
- cp:     Copy files
- mv:     Move files
- rm:     Remove files
- clear:  Clears the screen
- info:   Get information about a file
- run:    runs external python program
- sh:     run external sh script
- py:     Run python code
- pwd:    Show current directory
- mkdir:  Make directory
- rmdir:  Remove directory
- cd:     Change default directory
- exit:   Exit to Micropython shell

Actual external commands:

cpuclock, df, free, i2cscan, ifconfig, led, lineup, lshw, lsmod, mem_info, modules, ping, reboot, recovery, rmmod, sh.sh, test, touch, uhttpd, uptime, utelnetd, vi, wait, wget, wifi




Actual Development:

- /lib/grubs.py the first process in boot, will create .board file in /etc directory if does not exists, this file shoud be edited to acomodate all the board resources available, if the .board file exists, smolos process will read its content and will enable the resources to be used by the system, modules, external commands, etc.

- /lib/smolos.py is the next load, is the OS core, has internal and external commands (/bin directory), all commands will be moved to external commands to reduce the memory use.

- Actual implementation also can call simple shell scripts, including /etc/init.sh and /etc/rc.local, the start up scripts.

- Added editor from https://github.com/octopusengine/micropython-shell/tree/master

- Reduced memory usage to fit on esp8266

- Added recovery mode, to avoid load of start up failed commands

- Added env variables in scripts and python programs, export, echo, unset, sdata.getenv() ans sdata.setenv().

- ls now full functional, or so I hope.

TODO List:
- Enhance and move to external ls, cp, mv, etc. commands.
- Add grep, du, diff, find, tar, uname and hostname.
- Add threads
- 

Wishlist is open ;)

