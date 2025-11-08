# This script runs on boot. If it exists, the system is in normal mode.
# If it doesn't exist, the system is in recovery mode.

# Both internal and external commands can be used:
# > (Execute Python code)
# < (Print Python code execution output)

# Change configuration default values: 
> sdata.cache_enabled = False  # Enable filesystem cache (+ memmory needed)
> sdata.debug = False   # Debug mode
> sdata.log   = False   # No implemented yet

#cpufreq 160  # set mcu clock speed

# Welcome banner 
< "\033[1;33;44m", end=""
cat /etc/welcome.txt
< "\033[0m", end=""

# Choose your board model and layout
#loadboard /etc/upyOS-esp32c3_luatos.board
#loadboard /etc/upyOS-esp32c3_vcc_gnd.board
#loadboard /etc/upyOS-esp32s3_vcc_gnd.board
#loadboard /etc/upyOS-esp8266.board
#loadboard /etc/upyOS-esp32-wroom-32.board
#loadboard /etc/upyOS-rp2.board
loadboard /etc/upyOS-esp32c6_muse_labs.board

< "\\n"
lshw -b

< "\\n"*2
< "\033[1mMemory:"
free -h

< "\\n"*2
< "\033[1mStorage:"
df -h

# Test System Leds
led on 0             # Turn on led 0
sleep .05
led off 0            # Turn off led 0

led rgb 1            # Test rgb led in board (if board has one)

< "\\n"

# Wifi connection
#wifi sta on                     # Turn on wifi in cliente mode

#wifi sta status   
#wifi sta scan                   # Scan wifi APs

#wifi sta connect <SSID> <PASSWORD> 10 	# SSID PASS Timeout

#wifi sta status -n
#if $wa == False goto exit    # wifi active
#if $wc == False goto exit    # wifi connected

#ntpupdate es.pool.ntp.org    # Your ntp server

#date                         # Current date

#wifi sta ifconfig            # IPs information

#utelnetd start               # Start telnet server
#uftpd start                  # Start ftp server
#uhttpd start &               # Start http server

:exit

# Run an alternative local script if you don't want to modify 
# this one that will be changed in the updates.
test -f /local/init.sh > 0      # Check if script exists, save bool result in $0 env var
if $0 == True /local/init.sh
unset 0


