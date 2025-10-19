# AT modem script file (see /etc/modem.inf)
# Allows you to launch a script file or enter commands directly via the console.

from machine import UART, Pin
import time
import sdata
import utls

class ModemManager:
    def __init__(self, sctrl=True, scmds=True, sresp=True):
        self.sctrl = sctrl # Print ctrl messages
        self.scmds = scmds # Print cmds
        self.sresp = sresp # Print resp
        
        self._callback = None
    
    def setCallBack(self, callback): # add Callback
        self._callback = callback

    def reset(self, pin, wait=5):
        resetP = Pin(pin, Pin.OUT, value=1)  # HIGH default

        if self.sctrl:
            print("Reseting Modem...")
    
        resetP.value(0)
        time.sleep_ms(100) # 100ms pulse
        resetP.value(1)

        time.sleep(wait) # wait to ready
        if self.sctrl:
            print("Modem Ready")
            
    def createUART(self, id, baud, tx, rx):
        try:
            sdata.m0 = UART(id, baud, tx=Pin(tx), rx=Pin(rx))
            if self.sctrl:
                print("UART created\r\n\r\nOK")
            
        except Exception as ex:
            print("modem error, " + str(ex))
            return False
        time.sleep(1)  # Esperar a que el puerto se estabilice
        return True
        
    def atCMD(self, command, timeout=1.0):
        if sdata.m0 is None:
            print("The modem uart is not initialized, see help")
            return False
        
        # Limpiar buffer de entrada antes de enviar comando
        while sdata.m0.any() > 0:
            sdata.m0.read()
        
        command = command.replace("\\@", '"')
        
        # Enviar comando
        sdata.m0.write((command + "\r\n").encode('utf-8'))
        
        time.sleep(.2)
        
        # Esperar respuesta con timeout
        start_time = time.time()
        resp = ""
        response_complete = False
        
        while (time.time() - start_time) < timeout:
            if sdata.m0.any() > 0:
                line = sdata.m0.readline()
                if line:
                    line_str = line.decode('utf-8').strip()
                    resp += line_str + "\n"
                    
                    # Verificar si la respuesta está completa
                    # La mayoría de módems terminan con OK, ERROR, o prompt >
                    if "OK" in line_str or "ERROR" in line_str or ">" in line_str:
                        response_complete = True
                        break
            else:
                time.sleep(0.01)  # Pequeña pausa para no saturar el CPU
        
        # Si no hubo respuesta completa, dar un tiempo adicional
        if not response_complete:
            time.sleep(0.1)
            while sdata.m0.any() > 0:
                line = sdata.m0.readline()
                if line:
                    resp += line.decode('utf-8').strip() + "\n"
        
        if self.sresp:
            print(f"{resp}")
            
        # Llamar al callback con argumentos
        if self._callback:
            self._callback(command, resp)
        
        if "ERROR" in resp:
            return False
        
        return True

    def executeScript(self, file):
        with open(file, 'r') as archivo:
            while True:
                lin = archivo.readline()
                if not lin:  # Si no hay más líneas, salir del bucle
                    break
                if lin.strip() == "": 
                    continue   # Empty lines skipped
                if len(lin) > 0 and lin[0] == "#": 
                    continue # Commented lines skipped
                
                cmdl = lin.split("#")[0] # Left part of commented line
                # To be called from upyOS command line
                
                if self.scmds:
                    print(">> " + cmdl)
                
                tmp = cmdl.split()
                
                if tmp[0].lower() == "reset":
                    gpio  = int(tmp[1])  # Gpio reset pin in mcu
                    wait  = int(tmp[2])  # Modem wait to ready
                    self.reset(gpio, wait)
                elif tmp[0].lower() == "uart":
                    id   = int(tmp[1])  # uC Uart ID
                    baud = int(tmp[2])  # Baudrate
                    tx   = int(tmp[3])  # TX gpio
                    rx   = int(tmp[4])  # RX gpio
                    if not self.createUART(id, baud, tx, rx):
                        utls.setenv("?", "-1")
                        break
                elif tmp[0].lower() == "sleep":
                    if self.sctrl:
                        print(f"Waiting {tmp[1]}sec")
                    time.sleep(float(tmp[1]))
                else:
                    cmd = tmp[0]
                    timeout = 2.0  # Timeout por defecto aumentado
                    if len(tmp) > 1:
                        timeout = float(tmp[1])
                    if self.atCMD(cmd, timeout) == False:
                        utls.setenv("?", "-1")
                        break

def __main__(args):
    # Crear instancia del gestor de módem
    modem = ModemManager(sctrl=True, scmds=True, sresp=True)

    # Modem rest test
    #modem.reset(22, 3) # gpio 22 3 sec
    
    # Callback example
    #def callback(cmd, resp):
    #    print("Cmd from callback: " + cmd + "\n Response from callback:" + resp )
    #modem.setCallBack(callback)

    if len(args) == 0 or "--h" in args:
        print("Modem management utility\n")
        print("Usage:")
        print("\tExecute modem script: modem -f <file.inf>, See modem.inf in /etc directory")
        print("\tReset modem: modem -r <mcu gpio> <wait yo ready>")
        print("\tCreate serial uart (sdata.m0): modem -c <uart_id> <baud rate> <tx gpio> <rx gpio>")
        print("\tExecute AT command: modem <AT Command> <timeout>, Note: quotation marks must be sent as \\@")
        return
    
    if "-n" in args: # Print control
        modem.sctrl = False
        modem.scmds = False
        modem.sresp = False
        # Remover el flag -n de los argumentos
        args = [arg for arg in args if arg != "-n"]
   
    if args[0] == "-f":
        file = args[1]
        modem.executeScript(file)
        
    elif args[0] == "-r": # Reset modem
        gpio  = int(args[1])  # Gpio reset pin in mcu
        wait  = int(args[2])  # Modem wait to ready
        modem.reset(gpio, wait)
        
    elif args[0] == "-c": # Create uart (see --h)
        id   = int(args[1])  # uC Uart ID
        baud = int(args[2])  # Baudrate
        tx   = int(args[3])  # TX gpio
        rx   = int(args[4])  # RX gpio
        if not modem.createUART(id, baud, tx, rx):
            utls.setenv("?", "-1")
        
    else: # Executa AT command <cmd> <timeout>
        timeout = 2.0  # Timeout por defecto aumentado
        if len(args) > 1:
            timeout = float(args[1])
        if modem.atCMD(args[0], timeout) == False:
            utls.setenv("?", "-1")

# To call out upyos
if __name__ == "__main__":
    __main__(["-f", "modem.inf"])