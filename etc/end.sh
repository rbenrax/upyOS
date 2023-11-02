# Script triggered on system exit

test -p uhttpd
if $0 == 1 uhttpd stop

uftpd stop
utelnetd stop

wifi sta status -n
if $1 == 1 wifi sta disconnect -n
if $0 == 1 wifi sta off
