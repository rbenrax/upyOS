# Script triggered on system exit

test -p uhttpd
if $0 == 1 uhttpd stop

uftpd stop
utelnetd stop

wifi sta status -n
if $wa == True wifi sta disconnect -n
if $wc == True wifi sta off
