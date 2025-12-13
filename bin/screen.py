import sys
from machine import UART
import uselect
import sdata

def __main__(args):
    if "--h" in args:
        print("Modem (uart) direct access\nUsage: screen modem (modem0), see /etc/modem.inf")
        return

    device = "modem0"
    if len(args) == 1:
        device = args[0]
    
    if not hasattr(sdata, device):
        print(f"Device {device} not found")
        return
    uart = getattr(sdata, device)
    
    if not uart:
        print("Device not connected")
        return

    poll = uselect.poll()
    poll.register(sys.stdin, uselect.POLLIN)

    print(f"Connected to {device}, Ctrl+C to stop")
    line_buffer = ""

    try:
        while True:
            # Leer teclas una por una (solo si hay datos)
            if poll.poll(0):
                char = sys.stdin.read(1)
                if char:
                    if char == '\n' or char == '\r':
                        # Mostrar el salto de línea en local
                        sys.stdout.write('\r\n')
                        # Enviar la línea completa al UART con \r\n
                        if line_buffer:
                            uart.write(line_buffer + '\r\n')
                        else:
                            uart.write('\r\n')
                        line_buffer = ""  # reset buffer
                    else:
                        # Eco local y acumular
                        sys.stdout.write(char)
                        line_buffer += char

            # Leer y mostrar cualquier dato entrante del UART
            if uart.any():
                data = uart.read()
                if data:
                    try:
                        sys.stdout.write(data.decode('utf-8'))
                    except:
                        pass
                    
    except KeyboardInterrupt:
        print("\nProgram terminated")