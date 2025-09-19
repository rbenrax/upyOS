# Script triggered on system exit

test -p uhttpd > 0
if $0 == True uhttpd stop
unset 0

uftpd stop
utelnetd stop

wifi sta status -n
if $wa == True wifi sta disconnect -n
if $wc == True wifi sta off
