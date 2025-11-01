
# AT Modem utility and library (see /etc/modem.inf)
# Allows you to launch a script file or enter commands directly

from machine import UART, Pin, RTC
import time
import sdata
import utls

class ModemManager:
    def __init__(self, device="modem0"):
        
        self.device = device
        
        if not hasattr(sdata, device):
            setattr(sdata, device, None)
        self.modem = getattr(sdata, device)
        
        self.sctrl = False # Print ctrl messages
        self.scmds = False # Print cmds
        self.sresp = False # Print resp
        
        self._callback = None

        self.timming = False
        self.tini=0
        
    def setCallBack(self, callback): # add Callback
        self._callback = callback

    def resetHW(self, pin, wait=2):
        try:
            resetP = Pin(pin, Pin.OUT, value=1)  # HIGH default

            if self.sctrl:
                print("Reseting Modem...")
        
            resetP.value(0)
            time.sleep_ms(100) # 100ms pulse
            resetP.value(1)

            time.sleep(wait) # wait to ready
            if self.sctrl:
                print("Modem Ready")
        except Exception as ex:
            print("Modem reset error, " + str(ex))
            return False
        return True
            
    def createUART(self, id, baud, tx, rx):
        try:
            self.modem = UART(id, baud, tx=Pin(tx), rx=Pin(rx))
            if self.sctrl:
                print("UART created")
                
            setattr(sdata, self.device, self.modem)
            
        except Exception as ex:
            print("Modem error, " + str(ex))
            return False
        time.sleep(1)  # Esperar a que el puerto se estabilice
            
        return True
        
    def atCMD(self, command, exp="OK", timeout=2.0):

        if self.timming: 
            self.tini = time.ticks_ms()

        if self.modem is None:
            print("The modem uart is not initialized, see help")
            return False, ""

        timeout = timeout  * 1000

        while self.modem.any():
            self.modem.read()

        # Command execution Status
        cmdsts=True

        # Passthrow quotation marks
        command = command.replace("\\@", '"')

        # Enviar comando
        self.modem.write(command + '\r\n')
       
        if self.scmds:
            print(">> " + command)
       
        time.sleep(0.100)
       
        # Esperar respuesta
        resp = b""
        start_time = time.ticks_ms()
        
        #print("*****: " + str(timeout))
        
        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            if self.modem.any():
                data = self.modem.read()
                resp += data

                # TODO: Test: ERROR, FAIL, add: SEND OK, SEND FAIL, busy p...
                if exp == "OK" and "\r\nOK\r\n" in resp:
                    #print("*****: Brk 0")
                    break
                elif (exp == "ERROR" and "\r\nERROR\r\n" in resp) or "\r\nERROR\r\n" in resp:
                    cmdsts=False
                    #print("*****: Brk 1")
                    break
                elif (exp == "FAIL" and "\r\nFAIL\r\n" in resp) or "\r\nFAIL\r\n" in resp:
                    cmdsts=False
                    #print("*****: Brk 2")
                    break
                elif exp in resp:
                    #print("*****: Brk 3")
                    break

            time.sleep(0.02)
        
        time.sleep(0.05)
        
        decResp = resp.decode('utf-8')

        if self._callback:
           cbresp = self._callback(command, decResp)
           if cbresp != None:
               decResp = cbresp

        if self.sresp:
            print(f"<< {decResp}")
            
        if self.timming:            
            tfin = time.ticks_diff(time.ticks_ms(), self.tini)
            print(f"** Cmd: {command}: Time: {tfin}ms\n" )
        
        return cmdsts, decResp
    
    def rcvDATA(self, size=2048, encoded=True, timeout=5.0):
        
        if self.timming:
            ptini = time.ticks_ms()
        
        timeout = timeout  * 1000

        # Esperar respuesta
        resp = b""
        start_time = time.ticks_ms()
        
        #print("*rcv****: " + str(timeout))
        
        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            if self.modem.any():
                data = self.modem.read()
                resp += data
                start_time = time.ticks_ms() # restart if new data
                
                if len(resp) >= size:
                    resp += "\r\nCLOSED\r\n(more ...)"
                    #break
                
                if"\r\nCLOSED\r\n" in resp:
                    #print("*****: Brk rcv 1")
                    break

            time.sleep(0.02)
        
        if encoded:
            retResp = resp.decode('utf-8')
        else:
            retResp = resp
            
        if self.sresp:
            print(f"<< data: {retResp}")

        if self.timming:            
            ptfin = time.ticks_diff(time.ticks_ms(), ptini)
            print(f"## Tiempo rcv: {ptfin}ms" )

        return True, retResp
 
# ------ Command Implementations

    def test_modem(self):
        sts, ret = self.atCMD("AT")
        if sts:
            lines = ret.split('\n')
            return(lines[2])
        return "Error test"
    
    def get_version(self):
        sts, ret = self.atCMD("AT+GMR")
        if sts:
            return ret.replace("\r\nOK\r\n", "").replace("AT+GMR\r\n", "")
        
    def wifi_connect(self, ssid, password):
        # Configurar modo station
        sts, resp = self.atCMD("AT+CWMODE=1")
        if not sts:
            return False, resp
        
        time.sleep(1)
        
        # Conectar a WiFi
        cmd = f'AT+CWJAP="{ssid}","{password}"'
        sts, resp = self.atCMD(cmd, timeout=15.0)
        return sts, resp

    def wifi_disconnect(self):
        return self.atCMD("AT+CWQAP")

    def set_ntp_server(self, en=1, tz=1, ns1="es.pool.ntp.org", ns2="es.pool.ntp.org"):
                              #AT+CIPSNTPCFG=1,1,"es.pool.ntp.org","es.pool.ntp.org"
        sts, ret = self.atCMD(f'AT+CIPSNTPCFG={en},{tz},"{ns1}","{ns2}"')
        return sts

    def set_datetime(self):
        # Req. set_ntp_server
        sts, ret = self.atCMD("AT+CIPSNTPTIME?")
        if sts:
            fecha_str = ""
            for linea in ret.split('\n'):       
                if '+CIPSNTPTIME:' in linea:
                    fecha_str = linea.split(':', 1)[1]
                    break

            # Diccionarios para traducir abreviaciones
            dias_semana = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6, "Sun": 7}
            meses = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                     "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

            # Separar la cadena por espacios y limpiar huecos dobles
            partes = fecha_str.split()
            # Resultado típico: ['Thu', 'Jan', '1', '00:00:07', '1970']

            dia_semana_str, mes_str, dia_str, hora_str, anio_str = partes

            # Descomponer la hora
            hora, minuto, segundo = [int(x) for x in hora_str.split(":")]

            # Crear la tupla que espera el RTC
            fecha_rtc = (
                int(anio_str),          # Año
                meses[mes_str],         # Mes
                int(dia_str),           # Día
                dias_semana[dia_semana_str],  # Día de la semana (1=Lunes ... 7=Domingo)
                hora,                   # Hora
                minuto,                 # Minuto
                segundo,                # Segundo
                0                       # Subsegundos
            )

            # Configurar el RTC
            rtc = RTC()
            rtc.datetime(fecha_rtc)
            #return rtc.datetime()
            return sts

    def get_ip_mac(self, ip_mac):
        sts, ret = self.atCMD("AT+CIFSR")
        if sts:
            lines = ret.split('\n')
            if ip_mac.lower()=="ip":
                return(lines[1].split(",")[1])
            else:
                return(lines[2].split(",")[1])
            
        return "Error get iP/mac"
    
    # ------ Command Implementations
    
    # Tcp CMDs
    
    def create_conn(self, host, port, prot="TCP", keepalive=60):
        command = f'AT+CIPSTART="{prot}","{host}",{port},{keepalive}'
        sts, _ = self.atCMD(command, "CONNECT", 10.0)
        return sts
    
    def send_data(self, data):
        # Primero establecer longitud de datos
        length_cmd = f"AT+CIPSEND={len(data)}"
        sts, _ = self.atCMD(length_cmd, ">")
        if sts:
            # Enviar datos reales
            sts, ret = self.atCMD(data, "SEND OK")
            return sts
        return False
    
    def send_data_transparent(self, data):
        """Enviar datos en modo transparente"""
        # Primero establecer longitud
        length_cmd = f"AT+CIPSEND={len(data)}"
        sts, _ = self.atCMD(length_cmd, ">")
        if sts:
            # Enviar datos
            self.modem.write(data)
            sts, ret = self.atCMD("", "SEND OK")
            return sts
        return False
    
    def close_conn(self):
        """Cerrar conexión"""
        sts, _ = self.atCMD("AT+CIPCLOSE", "OK")
        return sts
    
    def enable_multiple_connections(self, enable=True):
        """Habilitar múltiples conexiones"""
        # Todo: Astk mode 1?
        mode = 1 if enable else 0
        return self.atCMD(f"AT+CIPMUX={mode}", "OK")

# ------ File script

    def executeScript(self, file):
        
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
                
                if tmp[0].lower() == "reset":
                    gpio  = int(tmp[1])  # Gpio reset pin in mcu
                    wait  = int(tmp[2])  # Modem wait to ready
                    self.resetHW(gpio, wait)
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
                        print(f"ctrl_log: Waiting {tmp[1]}sec")
                    time.sleep(float(tmp[1]))
                else:
                    cmd = tmp[0]
                    timeout = 2.0  # Timeout por defecto aumentado
                    exp = "OK"
                    if len(tmp) > 1:
                        timeout = float(tmp[1])
                    if len(tmp) > 2:
                        exp = tmp[2]
                    self.atCMD(cmd, exp, timeout)

# Command line tool
def __main__(args):
    # Crear instancia del gestor de módem
    modem = ModemManager() # Device def: sdata.modem0

    # Modem rest test
    #modem.reset(22, 3) # gpio 22 3 sec
    
    # Callback example
    #def callback(cmd, resp):
    #    print("Cmd from callback: " + cmd + "\n Response from callback:" + resp )
    #modem.setCallBack(callback)

    if len(args) == 0 or "--h" in args:
        print("Modem management utility for AT-ESP serial modem")
        print("Usage:\tExecute modem script: <ATmodem -f <file.inf>, See modem.inf in /etc directory")
        print("\tReset modem: ATmodem -r <mcu gpio> <wait to ready>")
        print("\tCreate serial uart: ATmodem -c <uart_id> <baud rate> <tx gpio> <rx gpio>")
        print("\tExecute AT command: ATmodem <AT Command> <timeout>, Note: quotation marks must be sent as \\@")
        print("\t-v verbose, -tm timmings")
        return
    
    if "-v" in args:
        modem.sctrl = True
        modem.scmds = True
        modem.sresp = True
        # Remover el flag -n de los argumentos
        args = [arg for arg in args if arg != "-v"]
        
    if "-tm" in args:
        modem.timming = True
        # Remover el flag -n de los argumentos
        args = [arg for arg in args if arg != "-tm"]
   
    if args[0] == "-f":
        file = args[1]
        modem.executeScript(file)
        
    elif args[0] == "-r": # Reset modem
        gpio  = int(args[1])  # Gpio reset pin in mcu
        wait  = int(args[2])  # Modem wait to ready
        modem.resetHW(gpio, wait)
        
    elif args[0] == "-c": # Create uart (see --h)
        id   = int(args[1])  # uC Uart ID
        baud = int(args[2])  # Baudrate
        tx   = int(args[3])  # TX gpio
        rx   = int(args[4])  # RX gpio
        if not modem.createUART(id, baud, tx, rx):
            utls.setenv("?", "-1")
        
    else: # Executa AT command <cmd> <timeout>
        timeout = 2.0  # Timeout por defecto aumentado
        exp="OK"¡¡
        if len(args) > 1:
            timeout = float(args[1])
        if len(args) > 2:
            exp = args[2]
            
        sts, resp = modem.atCMD(args[0], exp, timeout)
        if not sts:
            utls.setenv("?", "-1")

# To call out upyos
if __name__ == "__main__":
    __main__(["-f", "/local/dial.inf"])
