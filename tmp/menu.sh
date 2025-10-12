unset v1
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
