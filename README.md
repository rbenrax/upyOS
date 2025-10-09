# upyOS

*** Micropython 1.26.0 upgraded ***

upyOS is a modular flash Operating System for microcontrollers based on Micropython, giving the user POSIX-like environment, original idea by Krzysztof Krystian Jankowski and adapted by me.

[smolOS original github site](https://github.com/w84death/smolOS/tree/main)


The target is to get a common modular base to use stand alone microcontroller, avoiding monolithics programs, reuse modules and fun using it.

upyOS Installation:
```
	git clone https://github.com/rbenrax/upyOS.git

	cd upyOS
	mpremote fs -v cp main.py :main.py
	mpremote fs -r -v cp bin etc lib libx opt tmp www :

	mpremote
	Ctrl+D
```

Secreenshots of rp2040 module running upyOS:

![upyos01](media/upyos_01.png )

![upyos02](media/upyos_02.png )

Secreenshots of esp32c3 module running upyOS:

![upyos03](media/upyos_03.png )

![upyos04](media/upyos_04.png )

![upyos05](media/upyos_05.png )


upyOS explanation:

The target is to provide one more layer to micropython that allows us to manage a microcontroller in a similar way to what we use every day in a common computer, with the use of more simple programs that can be complemented in a more flexible way, obviously at cost of lower performance and efficiency, but giving more facilities and flexibility for those who start using microcontrollers.

On upyOS boot, /etc/init.sh will launch system start up commands, you can remove commands you don't need and make the boot as fast as you want, as well as, include commands or programs that you need run on statup.

On upyOS exit, /etc/end.sh will be lanched to send commans to disconnect os close processes.

The system can be extended with external commands and programs with the aim of keeping the memory footprint as low as possible, because the ram is quite small but the flash is big enough, every program to be executed must define a "def __main__(args):" function.

The sdata module contains all the system data, allowing access to the board configuration parameters, system configuration parameters, environment variables, etc., allowing access to these parameters between programs and scripts.

If system hungs in boot (ex. defective program), we can boot in recovery mode by sending "import utls" and "utls.recovery()" commands.

RP2040 has only two threads and is limited to this number, but ESP32 and others may have more. Python programs can be submitted in a separate thread by ending the command with '&' symbol, and asyncio programs may also be used."

Threads may be stopped by kill/killall commands, but then must be controlled in main loop inside the program, see examples in /opt directory.

I hope it is useful for you!, there are things to do, and to improve.

Directories structure:
- boot.py         Micropython statup file
- main.py         Micropython statup file (boot system)

```
      /bin        Commands and shell scripts
      /etc        Configuration files
      /libx       External libraries
      /lib        System implementations libraries
      /opt        Specific solution or add-on programs (not in path)
      /tmp        Temporary directory (to put what you don't know where to put :-)
      /www	  Web server directory
```

Internals commands:

- exit
- loadconfig: Load system config file
- loadboard:  Load board interfaces configuration file

Actual external commands:

cat, cd, clear, cp, cpufreq, date, decr, df, echo, env, export, fileup, find, free, grep, help, hold, i2cscan, ifconfig, incr, iperf3, kill, killall, led, ls, lshw, lsmod, mi, mkdir, mv, ntpupdate, ping, ps, pwd, read, reboot, reset, resume, rm, rmdir, rmmod, sensors, sh, si, sleep, test, touch, uftpd, uhttpd, unset, uptime, utelnetd, vi, wait, watch, wget, wifi.inf, wifi

Tested Boards:

esp32-c3
![luatos](media/luatos_CORE-ESP32_pinout.webp)

VCC-GND Studio YD-2040
![VCC-GND Studio](media/YD-2040-PIN.png)

GOOUUU ESP32 WROOM-32
![ESP32](media/ESP32-38-Pin-Pinout.jpg)

NodeMCU
![NodeMCU esp8266](media/Node-MCU-Pinout.png)

YD-ESP32-C3
![YD-ESP32-C3](media/YD-ESP32-C3-Pinout.jpg)

YD-ESP32-S3 with 8Mb PSRAM
![YD-ESP32-S3](media/YD-ESP32-S3-Pinout.jpg)


Actual Development:

- /lib/kernel.py is the first module loaded, is the OS core of de system, the first time create in /etc directory the .board file if doesn't exists, external commands are in /bin directory.

- Actual implementation also can call simple shell scripts, including /etc/init.sh and /etc/end.sh, the start up scripts and system down scripts.

- Added editor from https://github.com/octopusengine/micropython-shell/tree/master

- Reduced memory usage to fit on esp8266.

- Added recovery mode, to avoid load of start up failed commands or programs.

- Added environment variables in scripts and python programs, export, echo, unset sdata.getenv() ans sdata.setenv().

- ls command is now full functional, or so I hope.

- Now, commands translate environment variables.

- From command line prompt and shell scripts is possible input python code directly:
```
	">" command allow input python code:
	/ $: > import ftptiny
	/ $: > ftp = ftptiny.FtpTiny()
	/ $: > ftp.start()

	"<" command allow print any python expression:

	/ $: < sys.modules
	{'kernel': <module 'kernel' from '/lib/kernel.py'>, 'flashbdev': <module 'flashbdev' from 'flashbdev.py'>, 'network': <module 'network'>, 'sdata': <module 'sdata' from '/lib/sdata.py'>, 'utls': <module 'utls' from '/lib/utls.py'>}

	/ $: < 2+2
	4
```

- Management support for multiples threads and asyncio, tests availables (&, ps, kill, killall, wait, hold and resume):
```
      / $: /opt/thr_test &            # thread test
      / $: /opt/asy_test &            # asyncio test in new thread
```
- Shell script basic conditional execution, also are supported labels and goto instruction:

- example.sh
```
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
```
- menu.sh
```
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
```

- wifi startup sh script example (can be called from init.sh)
```
	#
	# WiFi connnection and and services startup
	#

	wifi sta on                      # Turn on wifi in cliente mode

	wifi sta status 

	#wifi sta scan                   # scan wifi APs

	wifi sta connect <SSID> <password> 10 # SSID PASS Timeout

	wifi sta status -n
	if $wa == False goto exit # wifi active
	if $wc == False goto exit # wifi connected

	ntpupdate es.pool.ntp.org

	date

	wifi sta ifconfig

	utelnetd start
	uftpd start
	uhttpd start &

	:exit
```
- end script example for stop running services:

# Script triggered on system exit

```
	test -p uhttpd > 0
	if $0 == True uhttpd stop
	unset 0

	uftpd stop
	utelnetd stop

	wifi sta status -n
	if $wc == True wifi sta disconnect -n
	if $wa == True wifi sta off
```

Script execution in boot:
![upyos06](media/upyos_06.png )

- loops in shell scripts!:
```
	:cont
	incr a
	if $a <= 5 goto cont
	echo $a

	:cont2
	decr a
	if $a > 4 goto cont2
	echo $a
```

- init.sh example with SSD1306 Oled display and start of process:
```
	# Init shell script 
	loadboard /etc/upyOS-esp32c3_vcc_gnd.board

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
	> sdata.d0 = ssd1306.SSD1306_SPI(128, 64, SPI(1), Pin(3), Pin(11), Pin(10)) # Gpios assignment
	> d0 = sdata.d0 	# Global reference for use in others programs

	> d0.fill(0)
	> d0.text(sdata.name + " " + sdata.version, 0, 0, 1)
	> d0.line(0, 15, 127, 15, 1)
	> d0.text("Iniciando...", 0, 16, 1)
	> d0.show()

	# Wifi sta
	wifi sta on                      	# Turn on wifi in cliente mode

	#wifi sta status
	#wifi sta scan                   	# scan wifi APs

	# Crear variable de entorno
	export essid <essid>
	export passw <password>

	> d0.text("Try.. " + utls.getenv("essid"), 0, 26, 1)  # Get environment Variable to show in display
	> d0.show()

	wifi sta connect $essid $passw 10 	# Connect to wifi router

	wifi sta status -n
	if $wa == False goto exit 		# wifi active
	if $wc == False goto exit 		# wifi connected

	> d0.text("Conected", 0, 36, 1)
	> d0.show()

	ntpupdate es.pool.ntp.org		# Time sync
	date

	> d0.text("ntpupdate", 0, 46, 1)
	> d0.text("Ready", 0, 56, 1)
	> d0.show()

	wifi sta ifconfig

	utelnetd start				# Start telset server
	uftpd start# 				# Start ftp server
	uhttpd start &				# Start web server

	#/local/dsp.py &			# Start utility program as thread

	:exit
	unset essid				# Remove enviroment variables
	unset passw
```


- upyOS remote development:
      - Start in remote mcu telnet service (utelnet start)
      - Start in remote mcu ftpserver service (uftpd start)
      - Install in local machine curlftpfs package
      - In local machine mount remote directory with "curlftpfs user@<mcuip> <local path>"
      - With Tonny you can develop in <local path>
      - Access with telnet to the mcu console ip to run commands and programs

- Added user and password authentication to access by telnet and ftp servers, user and password are stored in /etc/system.conf file, if no password is set then authentication is disabled.

- By starting utelnet and uftpd on boot, you can develop remotely from Android by using "Serial wifi terminal" and "Squircle CE" apps from Google Play, Termux is an excelent option too as telnet client.

- Added upgrade command for OTA upgrade from github repository.
```
	/ $: upgrade
	upyOS OTA Upgrade,
	Downloading upgrade list..., OK
	Confirm upyOS upgrade (y/N)? y
	Upgrading from upyOS github repository, wait...
	[.......................................................................................]OK
	100% Upgrade complete
	/ $:
```
- Added call caching to FS; on systems with low memory, it should be disabled in sdata.py. On systems with more memory (e.g., ESP32S3 with 8MB of PSRAM), enabling it speeds up file system access.

- creenshot of developping in a ESP32 mcu with upyOS + ![ftpfs](media/ftpfs.py) and telnet in Geany, VS code or others IDEs, local and remotely:

![Geany, VS code or others IDEs](media/upyos_07.png )
      
![ftpfs](media/ftpfs.py) Linux instalation (Optional):
```
	sudo apt-get install fuse libfuse-dev python3-pip
	pip3 install fusepy

	ftpfs use:

	# Mount
	mkdir ~/ftp_montado
	python3 ftpfs.py ftp.ejemplo.com ~/ftp_montado -u usuario -P pass

	# Directorio use
	ls ~/ftp_montado

	# Unmount
	fusermount -u ~/ftp_montado
```
	
- droid alternative: Squircle CE + termux Apps

  
TODO List:
- Add other usefull commands.
- Add Syslog

Wishlist is open ;)

