# Init file script in normal mode, if does not exists, we are in recovery mode and should exists init.rec

#clear
py print("\033[1;33;44m",end="")
cat /etc/wellcome.txt
py print("\033[0m",end="")

py print("\\n")
lshw -b

py print("\\n\033[1mMemory:")
free

py print("\\n\033[1mStorage:")
df

led on 0             # Turn on led 0
wait .1
led off 0            # Turn off led 0

#led rgb 1            # Test rgb led in board (if board has one)

