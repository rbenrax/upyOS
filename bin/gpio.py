import utls
from machine import Pin, ADC

def __main__(args):
    # Check for help
    if not args or "--h" in args:
        print("Get or set gpio value\nUsage: gpio [-a] <gpio> [value] [>[>] <var>/<file>]")
        print("  -a: Analog read mode")
        return

    # Separate redirection args
    redirection_args = []
    if ">>" in args:
        idx = args.index(">>")
        redirection_args = args[idx:]
        args = args[:idx]
    elif ">" in args:
        idx = args.index(">")
        redirection_args = args[idx:]
        args = args[:idx]

    # Check for analog flag
    analog_mode = False
    if "-a" in args:
        analog_mode = True
        args.remove("-a")

    if not args:
        print("Error: Missing pin number")
        return

    try:
        pin_num = int(args[0])
    except ValueError:
        print("Error: Pin must be an integer")
        return

    val = None
    
    try:
        if analog_mode:
            # Analog Read
            adc = ADC(Pin(pin_num))
            # Try read() first (standard for some ports), fallback to read_u16()
            try:
                if hasattr(adc, 'read'):
                    val = adc.read()
                else:
                    val = adc.read_u16()
            except Exception as e:
                # Some implementations might fail if not configured, try simple read_u16 if read fails
                 val = adc.read_u16()
        else:
            # Digital Mode
            if len(args) == 1:
                # Read
                val = Pin(pin_num, Pin.IN).value()
            else:
                # Write
                try:
                    target_val = int(args[1])
                    if target_val not in (0, 1):
                        print("Error: Value must be 0 or 1")
                        return
                    val = target_val
                    Pin(pin_num, Pin.OUT).value(val)
                except ValueError:
                    print("Error: Value must be an integer")
                    return
    except Exception as e:
        print(f"Error accessing pin {pin_num}: {e}")
        return

    # Output handling
    utls.outs(redirection_args, val)
