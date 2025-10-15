from machine import UART, Pin
import time
import sdata
import utls

def createUART(id, baud, tx, rx):
    try:
        sdata.m0 = UART(id, baud, tx=Pin(tx), rx=Pin(rx))
        print("UART created\r\n\r\nOK")
        
    except Exception as ex:
        print("modem error, " + str(ex))
        return False

    time.sleep(1)  # Esperar a que el puerto se estabilice
    return True
    
def atcmd(command, timeout=0.2):
    if sdata.m0 is None:
        print("The modem uart is not initialized, see help")
        return False
    
    #print(f"Enviando comando: {command}")
    sdata.m0.write((command + "\r\n").encode('utf-8'))
    time.sleep(timeout)
    
    resp = ""
    while sdata.m0.any() > 0:
        line = sdata.m0.readline().decode('utf-8')
        resp += str(line)

    print(f"{resp}")
    
    if "ERROR" in resp:
        return False

def __main__(args):
    
    if len(args) == 0 or "--h" in args:
        print("Modem management utility\nUsage:")
        print("\tEjecute modem script: modem -f <file.inf>, See modem.inf in /etc directory")
        print("\tCreate serial uart (sdata.m0): modem -c <uart_id> <baud rate> <tx gpio> <rx gpio>")
        print("\tEjecute AT command: modem <AT Command> <timeout>, Note: quotation marks must be sent as \@")
        return
        
    file=None
    if args[0]=="-f":
        file=args[1]
        with open(file, 'r') as archivo:
            while True:
                lin = archivo.readline()
                if not lin:  # Si no hay más líneas, salir del bucle
                    break
                if lin.strip()=="": continue   # Empty lines skipped
                if len(lin)>0 and lin[0]=="#": continue # Commanted lines skipped
                cmdl=lin.split("#")[0] # Left part of commented line

                # To be called from upyOS command line
                cmdl = cmdl.replace("\\@", '"')
                print(">>:" + cmdl)
                
                tmp = cmdl.split()
                
                #print(tmp)
                
                if tmp[0]== "uart":
                    id   = int(tmp[1])  # uC Uart ID
                    baud = int(tmp[2])  # Baudrate
                    tx   = int(tmp[3])  # TX gpio
                    rx   = int(tmp[4])  # RX gpio
                    if not createUART(id, baud, tx, rx):
                        utls.setenv("?", "-1")
                else:
                    cmd = tmp[0]
                    timeout=0.0
                    if len(tmp) > 1:
                        timeout = float(tmp[1])
                    if atcmd(cmd, timeout) == False:
                        utls.setenv("?", "-1")
                        break
        
    elif args[0]=="-c":
        id   = int(args[1])  # uC Uart ID
        baud = int(args[2]) # Baudrate
        tx   = int(args[3])   # TX gpio
        rx   = int(args[4])   # RX gpio
        if not createUART(id, baud, tx, rx):
            utls.setenv("?", "-1")
        
    else:
        timeout = 0.0
        if len(args) > 1:
            timeout = float(args[1])
        if atcmd(args[0], timeout) == False:
            utls.setenv("?", "-1")

# To call out upyos
if __name__ == "__main__":
    __main__(["-f", "modem.inf"])
