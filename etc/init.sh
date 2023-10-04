# This script file is the first script called in boot, this is normal mode, if does not exists,
# we are in recovery mode and should exists init.rec
# Internal and external commands can be used
# > (Execute Python code)
# < (Print the Python code execution)

#cpufreq 160 # If no board configuration, this and others commands can fail and should not be used 

< "\033[1;33;44m", end=""
cat /etc/wellcome.txt
< "\033[0m", end=""

loadboard    # You can choose do not load or use another board configuration, without param default
#loadboard /etc/upyOS-esp32c3.board
#loadboard /etc/upyOS-esp32-wroom-32.board

< "\\n"
lshw -b

< "\\n"*2
< "\033[1mMemory:"
free -h

< "\\n"*2
< "\033[1mStorage:"
df -h

#If no board configuration, nexts commands can fail and should not be used 
led on 0             # Turn on led 0
sleep .05
led off 0            # Turn off led 0

led rgb 1            # Test rgb led in board (if board has one)

