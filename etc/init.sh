# This script runs at boot. If it exists, the system is in normal mode.
# If it does not exist, the system enters recovery mode.

# Both internal and external commands can be used:
# >  (Execute Python code)
# <  (Print Python code execution output)

# Change default configuration values:
> sdata.cache_enabled = False  # Enable filesystem cache (requires more memory)
> sdata.debug = False          # Debug mode
> sdata.log   = False          # Not implemented yet

#cpufreq 160  # Set MCU clock speed

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

# Test system LEDs
led on 0              # Turn on LED 0
sleep .05
led off 0             # Turn off LED 0

led rgb 1             # Test the board's RGB LED (if available)

< "\\n"

# WiFi connection for mcus with integrated connectivity:

#wifi sta on                     # Enable WiFi in station mode

#wifi sta status   
#wifi sta scan                   # Scan for WiFi access points

#wifi sta connect <SSID> <PASSWORD> 10   # SSID PASS Timeout

#wifi sta status -n
#if $wa == False goto exit       # WiFi active?
#if $wc == False goto exit       # WiFi connected?

#ntpupdate es.pool.ntp.org       # Your NTP server

#date                            # Current date/time

#wifi sta ifconfig               # IP information


# -- ATTENTION: Only for MCUs without integrated connectivity ---------------- #

# Using an ESP8266 with ESP-AT firmware (see /etc/modem.inf)

#atmodem -r 22 1     # Reset modem
#sleep 3

#atmodem -c 1 115200 4 5 modem0 -v -tm  # Initialize UART and modem: -v verbose, -tm show timings
#atmodem AT+UART_CUR=115200,8,1,0,3     # Enable hardware flow control on ESP module

# Optional: Execute an additional or complementary AT command script
#echo "Executing modem script..."
#atmodem -f /local/dial.inf

# Connecting using external modem (if you wish, you can do a .py program)
#> from esp_at import ModemManager
#> mm = ModemManager()
#< f"Modem: {mm.device}"
#< mm.get_version()

#< "Connecting WiFi..."
#> mm.wifi_set_mode(1); mm.wifi_connect("SSID", "PASSWORD")

#< f"WiFi status: {mm.wifi_status()}"
#< "NTP update..."
#> mm.set_ntp_server(); mm.set_datetime(); del mm
#date

# Example usage of MQTT command with AT modem:
#export h = 192.168.2.132
#atmqttc pub -h $h -t "home/bedroom/temp" -m "25"
#atmqttc sub -t "#"
#atmqttc listsub -t "#"
#atmqttc listen

# -- ATTENTION ---------------------------------------------------------------- #

# Example usage of MQTT commands for MCUs with integrated connectivity:

#export h = 192.168.2.132
#mqttc pub -h $h -t "home/bedroom/temp" -m "25"
#mqttc sub -t "#"
#mqttc listsub -t "#"

# Start integrated services

#utelnetd start               # Start Telnet server
#uftpd start                  # Start FTP server
#uhttpd start &               # Start HTTP server

:exit

# Run an alternative local script if you prefer not to modify
# this one (it may be overwritten during updates).
test -f /local/init.sh > 0       # Check if script exists and store result in $0
if $0 == True /local/init.sh
unset 0
