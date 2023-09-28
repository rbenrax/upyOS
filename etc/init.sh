# This script file is the first script called in boot, this is normal mode, if does not exists,
# we are in recovery mode and should exists init.rec
# Internal and external commands can be used
# > (Execute Python code)
# < (Print the Python code execution)

cpufreq -turbo

< "\033[1;33;44m", end=""
cat /etc/wellcome.txt
< "\033[0m", end=""

< "\\n"
lshw -b

< "\\n"*2
< "\033[1mMemory:"
free -h

< "\\n"*2
< "\033[1mStorage:"
df -h

led on 0             # Turn on led 0
sleep .05
led off 0            # Turn off led 0

led rgb 1            # Test rgb led in board (if board has one)

