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
    
    uart = None
    if not hasattr(sdata, device):
        print(f"Device {device} not found")
        return
    else:
        uart = getattr(sdata, device)
    
    if not uart:
        print("Device no connected")
        return

    # Configurar poll para entrada estándar (consola)
    poll = uselect.poll()
    poll.register(sys.stdin, uselect.POLLIN)

    print(f"Connected to {device}, Ctrl+C to stop")

    try:
        while True:
            # Verificar si hay datos en la consola (entrada estándar)
            if poll.poll(0):
                data_console = sys.stdin.readline().strip()
                if data_console:
                    uart.write(data_console + '\r\n')
                    print(f"{data_console}")
            
            # Verificar si hay datos en UART
            if uart.any():
                data_uart = uart.read()
                if data_uart:
                    print(f"{data_uart.decode('utf-8').strip()}")
                    
    except KeyboardInterrupt:
        print("\nProgram terminated")
