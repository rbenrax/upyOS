# Script triggered on system exit

wifi sta status
if $1 == 1 wifi sta disconnect
if $0 == 1 wifi sta off