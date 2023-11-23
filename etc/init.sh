# This script is called in boot, this is normal mode, 
# if does not exists, then recovery mode

# Internal and external commands can be used
# > (Execute Python code)
# < (Print the Python code execuion)

# > sdata.debug=False    # Debug mode

#cpufreq 133  # set mcu clock speed

< "\033[1;33;44m", end=""
cat /etc/wellcome.txt
< "\033[0m", end=""

# loadboard    # You can choose load different boards configuration, without param, default board
#loadboard /etc/upyOS-esp32c3_luatos.board
loadboard /etc/upyOS-esp32c3_vcc_gnd.board
#loadboard /etc/upyOS-esp32s3_vcc_gnd.board
#loadboard /etc/upyOS-esp8266.board
#loadboard /etc/upyOS-esp32-wroom-32.board
#loadboard /etc/upyOS-rp2.board

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
# Wifi
#wifi sta on                      # Turn on wifi in cliente mode

#wifi sta status   
#wifi sta scan                   # scan wifi APs

#wifi sta connect DIGIFIBRA-cGPRi <password> 10 # SSID PASS Timeout

#wifi sta status -n
#if $0 == 0 goto exit
#if $1 == 0 goto exit

#ntpupdate 150.214.5.121  
#ntpupdate es.pool.ntp.org

#date

#wifi sta ifconfig

#utelnetd start
#uhttpd start &
#uftpd start &

:exit

# Run local script
test -f /local/w.sh       # Check if script exists, save result in $0 env var
if $0 == 1 /local/w.sh


