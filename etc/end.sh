# Script triggered on system exit

test -p uhttpd > 0
if $0 == True uhttpd stop
unset 0
