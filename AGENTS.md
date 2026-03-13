# AGENTS.md - upyOS Development Guide

## Overview

upyOS is a modular flash Operating System for microcontrollers based on **MicroPython**. It provides a POSIX-like environment for microcontrollers (ESP32, ESP8266, RP2040, etc.).

This file provides guidelines for agents working on this codebase.

---

## Project Structure

```
/bin/      - Commands (each .py file is a command)
/lib/      - Core libraries (kernel.py, proc.py, utls.py, sdata.py)
/libx/     - Extended libraries
/etc/      - Configuration files, board definitions, init scripts
/opt/      - Optional programs and examples
/tmp/      - Temporary files
/www/      - Web interface files
boot.py    - Bootloader
main.py    - Main entry point
```

---

## Build, Lint, and Test Commands

### Running on Hardware

upyOS runs on microcontrollers and doesn't have a traditional build system. Use `mpremote` to deploy:

```bash
# Connect to board via USB/Serial
mpremote connect /dev/ttyUSB0 mount

# Or via WiFi (if already running)
mpremote connect 192.168.1.100 mount

# Soft reset
mpremote reset
```

### Testing Individual Commands

Commands are tested by running them on the hardware. To test a specific command:

```bash
# Via mpremote shell
mpremote connect /dev/ttyUSB0 exec "import your_command; your_command.__main__(['arg1', 'arg2'])"

# Or from upyOS shell once running
your_command arg1 arg2
```

### Test Files Location

- `/bin/test.py` - Unix-like `test` command (file/process/gpio checking)
- `/opt/run_test.py` - Example test program template
- `/opt/thr_test.py` - Threading test example
- `/opt/asy_test.py` - Async test example
- `/opt/dht_test.py` - DHT sensor test example

### Manual Testing Workflow

1. Deploy files to board: `mpremote connect <device> mount`
2. Test manually via shell or programmatically
3. Use `sdata.debug = True` in `/lib/sdata.py` for verbose error output
4. Check `/etc/system.conf` for system configuration

---

## Code Style Guidelines

### General Principles

- **MicroPython compatibility**: Use only modules available in MicroPython (not standard Python)
- **Memory efficiency**: Optimize for constrained microcontroller environments
- **Error handling**: Always handle exceptions gracefully
- **Documentation**: Include `--h` help text in every command

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Commands | lowercase, `.py` extension | `wifi.py`, `gpio.py` |
| Classes | PascalCase | `class Proc:`, `class upyOS:` |
| Functions | lowercase with underscores | `def file_exists():`, `def run_cmd():` |
| Constants | UPPERCASE | `MONTH`, `WEEKDAY`, `AUTHMODE` |
| Private vars | leading underscore | `_network_available` |
| Global state | via `sdata` module | `sdata.procs`, `sdata.debug` |

### Imports

Order imports by category (MicroPython standard library first, then local modules):

```python
# 1. Standard MicroPython modules (alphabetical)
import sys
import utime
import uos

# 2. Third-party / external (network, machine, etc.)
from machine import Pin, UART
import network

# 3. Local modules (utls, sdata, proc)
import utls
import sdata
import proc
```

### Module Structure

Each command file should follow this pattern:

```python
# Brief description
import utls
import sdata

def __main__(args):
    # Main entry point (required for command execution)
    if "--h" in args:
        print("Help text explaining usage")
        return
    
    # Command logic here

if __name__ == "__main__":
    __main__([])
```

### Core Library Structure

Core modules (`/lib/`):

```python
# /lib/kernel.py
class upyOS:
    def __init__(self, boot_args):
        # Initialize system
        
    def run_cmd(self, fcmd):
        # Execute command
        
# /lib/proc.py  
class Proc:
    def run(self, isthr, ext, cmd, args):
        # Process execution
        
# /lib/sdata.py - Global state (simple module, not class)
name = ""
version = ""
debug = True
procs = []

# /lib/utls.py - Utility functions
def file_exists(filename):
    # ...
```

### Error Handling

```python
try:
    # Risky operation
    result = some_function()
except OSError:
    # Handle filesystem errors
    print("File not found")
except ImportError:
    # Handle missing modules
    print("Module not available on this platform")
except Exception as e:
    # Catch-all with debug output
    print(f"Error: {e}")
    if sdata.debug:
        sys.print_exception(e)
```

### Command-Line Argument Parsing

Use simple pattern matching (no argparse):

```python
def __main__(args):
    if "--h" in args:
        print("Usage: cmd <arg> [-o option]")
        return
        
    path = ""
    mode = "-l"
    
    if len(args) >= 1:
        if args[0].startswith("-"):
            mode = args[0]
            path = args[1] if len(args) > 1 else ""
        else:
            path = args[0]
            mode = args[1] if len(args) > 1 else "-l"
```

### MicroPython-Specific Guidelines

| Standard Python | MicroPython |
|-----------------|--------------|
| `time` | `utime` |
| `os` | `uos` |
| `print()` | `print()` (MicroPython supports keyword args) |
| `dict.keys()` | Use `in dict` for membership tests |
| f-strings | f-strings supported in MicroPython 1.12+ |

### Performance Tips

- Use `stat()` once and cache results
- Minimize string operations in loops
- Use `try/except` for flow control (faster than `if`)
- Avoid excessive recursion
- Use generators for large datasets

---

## Development Workflow

### Adding a New Command

1. Create `/bin/your_command.py`
2. Implement `__main__(args)` function
3. Add help with `--h` argument
4. Test on hardware

### Adding to Kernel

Internal commands go in `kernel.py` under `user_commands`:

```python
self.user_commands = {
    "exit": self.exit,
    "loadconfig": self.loadconfig,
    # Add new command here
}
```

### Debugging

```python
# Enable debug mode
sdata.debug = True

# Enable logging  
sdata.log = True

# Print exceptions
sys.print_exception(ex)
```

---

## Important Files Reference

| File | Purpose |
|------|---------|
| `/lib/kernel.py` | Main OS kernel and command execution |
| `/lib/proc.py` | Process management |
| `/lib/utls.py` | Utility functions |
| `/lib/sdata.py` | Global system data |
| `/etc/system.conf` | System configuration |
| `/etc/init.sh` | Startup script |
| `/etc/default.board` | Board configuration |
