import utls
from machine import Pin

def __main__(args):
    if not args or "--h" in args:
        print("Get or set gpio value\nUsage: gpio --h <gpio> [value] [>[>] <var>/<file>]")
        return

    # Detectar redirección con > o >>
    if ">" in args:
        i = args.index(">")
    elif ">>" in args:
        i = args.index(">>")
    else:
        i = -1

    nargs = args[:i] if i > 0 else args

    # Obtener o establecer valor del pin GPIO
    pin = int(nargs[0])
    if len(nargs) == 1:
        val = Pin(pin, Pin.IN).value()
    else:
        val = 1 if int(nargs[1]) > 0 else 0
        Pin(pin, Pin.OUT).value(val)

    # Salida a archivo, variable, etc.
    utls.outs(args, val)
