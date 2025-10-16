# Script triggered on system exit

test -p uhttpd > 0
if $0 == True uhttpd stop
unset 0

wifi sta status -n
if $wc == uftpd stop
if $wc == utelnetd stop
if $wc == True wifi sta disconnect -n
if $wa == True wifi sta off
