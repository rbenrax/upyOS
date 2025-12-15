from machine import WDT
import time
import sys

def __main__(args):
    doc = """
    watchdog - Watchdog using persistent WDT(id=0)
    Usage:
      watchdog -t SECONDS [-d SECONDS] -q  # Start watchdog (id=0)
      watchdog -f -q                       # Feed existing watchdog (id=0)
      watchdog --h                         # Show help

    Options:
      -t SECONDS    Set timeout and start WDT(id=0)
      -d SECONDS    Delay before activation (only with -t)
      -f            Feed WDT(id=0)
      --h           Show this help

    Note: On ESP32, WDT(id=0) is persistent. -f works only after -t has been used.
    """
    
    if len(args) == 0 or "--h" in args:
        print(doc)
        return

    # Handle feed command
    if "-f" in args:
        try:
            # Re-acquire WDT instance with same id (0)
            wdt = WDT(id=0)
            wdt.feed()
            if not "-q" in args:
                print("Watchdog fed.")
        except Exception as e:
            print(f"Error feeding watchdog (was it started?): {e}")
        return

    # Handle start command
    timeout = None
    delay = 0
    i = 0

    while i < len(args):
        arg = args[i]
        if arg == "-t":
            if i + 1 >= len(args):
                print("Error: -t requires a timeout value (seconds)")
                return
            try:
                timeout = int(args[i + 1])
                if timeout <= 0:
                    print("Error: timeout must be a positive integer")
                    return
            except ValueError:
                print("Error: timeout must be an integer")
                return
            i += 2
        elif arg == "-d":
            if i + 1 >= len(args):
                print("Error: -d requires a delay value (seconds)")
                return
            try:
                delay = int(args[i + 1])
                if delay < 0:
                    print("Error: delay must be >= 0")
                    return
            except ValueError:
                print("Error: delay must be an integer")
                return
            i += 2
        else:
            print(f"Error: unknown option '{arg}'")
            return

    if timeout is None:
        print("Error: Use -t SECONDS to start, or -f to feed an existing watchdog.")
        return

    if delay > 0:
        print(f"Delaying watchdog activation for {delay} seconds...")
        time.sleep(delay)

    try:
        # Create WDT with id=0 (persistent on ESP32)
        wdt = WDT(id=0, timeout=timeout * 1000)
        if not "-q" in args:
            print(f"Watchdog started (id=0) with timeout = {timeout} seconds")
            print("Use 'watchdog -f' to feed it later.")
    except Exception as e:
        print(f"Error starting watchdog: {e}")
        sys.print_exception(e)