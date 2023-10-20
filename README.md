# upyOS

upyOS is a modular flash Operating System for microcontrollers based in Micropython, giving the user POSIX-like environment, original idea by Krzysztof Krystian Jankowski and adapted by me.

[smolOS original github site](https://github.com/w84death/smolOS/tree/main)


The target is to get a common modular base to use stand alone microcontroller, and fun using it. 

Secreenshots of rp2040 module running upyOS:

![upyos01](media/upyos_01.png )

![upyos02](media/upyos_02.png )

Secreenshots of esp32c3 module running upyOS:

![upyos03](media/upyos_03.png )

![upyos04](media/upyos_04.png )

![upyos05](media/upyos_05.png )


upyOS Help:

Adapted by rbenrax, source available in https://github.com/rbenrax/upyOS, based in Krzysztof Krystian Jankowski work available in smol.p1x.in/os/

Explanation:

The objective is to provide one more layer to micropython that allows us to manage a microcontroller in a similar way to what we use every day in a common computer, with the use of more simple programs that can be complemented in a more flexible way, obviously at the cost of lower performance and efficiency, but giving more facilities for those who start using microcontrollers.

In main.py we can launch grub or upyOS directly (see files).

Grub will create in /etc dir a file (if doesn't exists) for configure the specific board pins, gpios and other parameters, you can remove unused parameter to optimize the memory use, also allow stop the system boot if any program hung the load.

In upyOS boot, two shell scripts are executed, init.sh and rc.local, init.sh will launch system start up commands, and rc.local programa and commands specifics for a user solution, you can remove the commands you don't need and make the boot as fast as you want, as well as include commands or programs that you need.

Exists internal and external commands, and internal and externals shell scripts, internal located in /bin directory and are exceuted without extention, external can be located in any directory and are executed directly, external commands are self-explanatory and some have help (--h).

The system can be extended with more external commands and programs with the aim of keeping the memory footprint as low as possible, because the ram is quite small but the flash is big enough.

The sdata module contains all the system data, allowing access to the board configuration parameters, system configuration parameters, environment variables, etc., allowing access to these parameters between programs and scripts.

If system hungs in boot (ex. defective program), we can delete init.sh, then the system wil boot in recovery mode, also we can use recovery command in any time, which moves init.sh to init.rec and viceversa.

RP2040 has only two threads and is limited to this number, but ESP32 and others may have more. Python programs can be submitted in a separate thread by ending the command with '&' symbol, and asyncio programs may also be used."

Threads may be stopped by kill command, but then must be controlled in main loop inside the procces, see examples in /opt directory.

I hope it is useful for you!, there are things to do, and to improve.

Directories structure:
- boot.py         Micropython statup file
- main.py         Micropython statup file (boot system)

      /bin        Commands and shell scripts
      /etc        Configuration files
      /libx       External libraries
      /lib        System implementations libraries
      /opt        Specific solution or add-on programs (not in path)
      /tmp        Temporary directory (to put what you don't know where to put :-)


Internals commands:

- loadconfig: Load system config file
- loadboard:  Load board interfaces configuration file
- r:          Repeat last command

Actual external commands:

cat, cd, clear, cp, cpufreq, date, decr, df, echo, env, export, fileup, find, free, grep, help, i2cscan, ifconfig, incr, iperf3, kill, killall, led, ls, lshw, lsmod, mi, mkdir, mv, ntpupdate, ping, ps, pwd, read, reboot, recovery, reset, rm, rmdir, rmmod, sensors, sh, si, sleep, test, touch, uhttpd, unset, uptime, vi, wait, watch, wget, wifi.inf, wifi

esp32-c3
![luatos](media/luatos_CORE-ESP32_pinout.webp)

VCC-GND Studio YD-2040
![VCC-GND Studio](media/YD-2040-PIN.png)

GOOUUU ESP32 WROOM-32
![ESP32](media/ESP32-38-Pin-Pinout.jpg)

NodeMCU
![NodeMCU esp8266](media/Node-MCU-Pinout.png )


Actual Development:

- /lib/grubs.py the first process in boot, will create .board file in /etc directory if does not exists, this file shoud be edited to acomodate all the board resources available, if the .board file exists, upyOS process will read its content and will enable the resources to be used by the system, modules, external commands, etc.

- /lib/kernel.py upyos class is the next load, is the OS core, has internal and external commands (/bin directory), all commands will be moved to external commands to reduce the memory use.

- Actual implementation also can call simple shell scripts, including /etc/init.sh and /etc/rc.local, the start up scripts.

- Added editor from https://github.com/octopusengine/micropython-shell/tree/master

- Reduced memory usage to fit on esp8266

- Added recovery mode, to avoid load of start up failed commands

- Added environment variables in scripts and python programs, export, echo, unset sdata.getenv() ans sdata.setenv().

- ls command is now full functional, or so I hope.

- Now commands translate environment variables.

- From command line prompt and shell scripts is possible input python code directly:

      ">" command allow input python code:
      / $: > import ftptiny
      / $: > ftp = ftptiny.FtpTiny()
      / $: > ftp.start()
      
      "<" command allow print any python expression:
      
      / $: < sys.modules
      {'kernel': <module 'kernel' from '/lib/kernel.py'>, 'flashbdev': <module 'flashbdev' from 'flashbdev.py'>, 'network': <module 'network'>, 'sdata': <module 'sdata' from '/lib/sdata.py'>, 'utls': <module 'utls' from '/lib/utls.py'>}
      
      / $: < 2+2
      4

- Management support for multiples threads and asyncio, tests availables (&, kill, killall, wait):
  
      / $: /opt/thr_test &            # thread test
      / $: /opt/asy_test &            # asyncio test in new thread
  
- Shell script basic conditional execution:

example.sh

      export var1 5   # Set variable var1 to "5" (variables can also be accesed from Python programs and embedded Python)
      if $var1 != 5 skip 3 # Skip 3 lines if comparison is true (will continue in 4, 5, etc)
      < 1
      < 2
      < skip 2
      < 4
      < 5
      if $var1 == 3 return        # Ends shell script
      if $var1 == 5 run watch ps -t 5 # Launch command "watch ps" every 5 seconds
      if $var1 == 6 run asy_test &    # Summit asy_test process

  menu.sh
  
      :loop
      clear
      < "Options Menu"
      < ""
      < "Option 1 160MHz"
      < "Option 2 240Mhz"
      < "Option 3 return"
      < "Option 0 exit"
      < ""
      echo "Last option: " $v1
      read v1 "Enter option: "
      if $v1 == 1 cpufreq 160
      if $v1 == 2 cpufreq 240
      if $v1 == 3 return
      if $v1 != 0 goto loop
      exit

sh example script

      #
      # upyos sh script example
      #

      # Wifi sta
      wifi sta on                       # Turn on wifi in cliente nic

      #wifi sta scan                    # scan wifi APs

      wifi sta connect DIGIFIBRA-cGPRi password 10 # Connect to wifi router <ssid> <password> <timeout>

      wifi sta status                   # save two env vars with the status status
      if $0 == 0 goto exit             # $0 = enabled/disabled
      if $1 == 0 goto exit             # $1 = connected/disconnected

      ntpupdate es.pool.ntp.org         # ntp time update
      date                              # show current date and time

      wifi sta ifconfig                 # sta ip config status
      
      :exit                            # If error label target
      echo exit
      wifi sta off                      # disable nic

      exit

Script execution in boot:
![upyos06](media/upyos_06.png )

And loops!:

      :cont
      incr a
      if $a <= 5 goto cont
      echo $a

      :cont2
      decr a
      if $a > 4 goto cont2
      echo $a

TODO List:
- Add diff, tar, uname, read and other usefull commands.
- Bluetooth support
- Add Syslog
- Upgrade procedure
- jobq?

Wishlist is open ;)

