# Script triggered on system exit

utelnetd stop

test -p uftpd
if $0 == 1 uftpd stop

test -p uhttpd
if $0 == 1 uhttpd stop

wifi sta status -n
if $1 == 1 wifi sta disconnect -n
if $0 == 1 wifi sta off
