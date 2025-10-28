# Global system data module

name    = "" # System name
version = "" # Current version
sid     = 0  # System identification
initime = 0  # Start up time

# FS cache control (Default false, if speed is required, may be enabled)
cache_enabled = False
debug   = True
log     = False

upyos = None # Kernel instance
board = {}   # Board model spec
sysconfig={} # System configuration

_pid=0
procs=[] # Running proccesses

# Drivers
d0 = None # Global ref to display 0
