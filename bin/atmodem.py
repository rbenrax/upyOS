
# AT Modem utility (see /etc/modem.inf)
# Allows you to launch a script file on /etc/init.sh or enter commands directly by terminal.

from esp_at import ModemManager
import time
import sdata
import utls
import sys

def executeScript(mm, file):
    
    if not utls.file_exists(file):
        print(f"File {file} not found")
        return
    
    with open(file, 'r') as archivo:
        while True:
            lin = archivo.readline()
            
            if not lin:  # Si no hay más líneas, salir del bucle
                break
            
            if lin.strip() == "": continue   # Empty lines skipped
            if lin.lstrip().startswith("#"): continue # Commanted lines skipped
            cmdl = lin.split(" #")[0] # Left part of commented line
            tmp = cmdl.split()
            executeLine(mm, tmp)
            
def executeLine(mm, tmp):

    if tmp[0].lower() == "reset" or tmp[0].lower() == "-r":
        gpio  = int(tmp[1])  # Gpio reset pin in mcu
        wait  = int(tmp[2])  # Modem wait to ready
        mm.resetHW(gpio, wait)

    elif tmp[0].lower() == "uart" or tmp[0].lower() == "-c":

            id   = int(tmp[1])  # uC Uart ID
            baud = int(tmp[2])  # Baudrate
            tx   = int(tmp[3])  # TX gpio
            rx   = int(tmp[4])  # RX gpio
            if len(tmp) == 6:
               mm.device = tmp[5] # Modem name (modem0)

            if len(tmp) > 6:
                rts=int(tmp[6])
                cts=int(tmp[7])
                txbuf=256
                rxbuf=1024
                tout=0
                tout_char=0
                flow_type=tmp[8] # r, s, rs, off

            mm.createUART(id, baud, tx, rx, mm.device,
                          rts, cts,
                          txbuf, rxbuf,
                          tout, tout,
                          flow_type)

    elif tmp[0].lower() == "sleep":
        if mm.sctrl:
            print(f"** Waiting {tmp[1]}sec\n")
        time.sleep(float(tmp[1]))
        
    elif tmp[0].lower() == "echo":
        print(" ".join(tmp[1:])) # TODO: Translate env vars
        
    else:
        cmd = tmp[0]
        timeout = 2.0  # Timeout por defecto aumentado
        exp = "OK"
        if len(tmp) > 1:
            timeout = float(tmp[1])
        if len(tmp) > 2:
            exp = tmp[2]
        mm.atCMD(cmd, timeout, exp)

# Command line tool
def __main__(args):

    if len(args) == 0 or "--h" in args:
        print("Modem management utility for AT-ESP serial modem")
        print("Usage:\tExecute modem script: atmodem -f <file.inf>, See /etc/modem.inf")
        print("\tReset modem: atmodem -r <mcu gpio> <wait to ready>")
        print("\tCreate serial uart: atmodem -c <uart_id> <baud rate> <tx gpio> <rx gpio> [<modemname (modem0)>]")
        print("\tExecute AT command: atmodem <AT Command> <timeout> <expected resp>, Note: quotation marks must be sent as \\@")
        print("\t-v verbose, -tm timings")
        return
    
    try:
        # Create a modem manager instance
        modem = ModemManager() # Def device sdata.modem0
        
        if "-v" in args:
            modem.sctrl = True
            modem.scmds = True
            modem.sresp = True
            # Remover el flag -n de los argumentos
            args = [arg for arg in args if arg != "-v"]
            
        if "-tm" in args:
            modem.timing = True
            # Remover el flag -n de los argumentos
            args = [arg for arg in args if arg != "-tm"]
       
        if args[0] == "-f":
            file = args[1]
            executeScript(modem, file)
        else:
            executeLine(modem, args)
            
    except Exception as ex:
        print("atmodem error, " + str(ex))
        sys.print_exception(ex)
