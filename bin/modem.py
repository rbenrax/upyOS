
# AT Modem utility and library (see /etc/modem.inf)
# Allows you to launch a script file or enter commands directly via the console, and function library.

from machine import UART, Pin
import time
import sdata
import utls

class ModemManager:
    def __init__(self, sctrl=False, scmds=False, sresp=False):
        self.sctrl = sctrl # Print ctrl messages
        self.scmds = scmds # Print cmds
        self.sresp = sresp # Print resp
        
        self._callback = None
    
    def setCallBack(self, callback): # add Callback
        self._callback = callback

    def resetHW(self, pin, wait=5):
        resetP = Pin(pin, Pin.OUT, value=1)  # HIGH default

        if self.sctrl:
            print("ctrl_log: Reseting Modem...")
    
        resetP.value(0)
        time.sleep_ms(100) # 100ms pulse
        resetP.value(1)

        time.sleep(wait) # wait to ready
        if self.sctrl:
            print("ctrl_log: Modem Ready")
            
    def createUART(self, id, baud, tx, rx):
        try:
            sdata.m0 = UART(id, baud, tx=Pin(tx), rx=Pin(rx))
            if self.sctrl:
                print("UART created\r\n\r\nOK")
            
        except Exception as ex:
            print("Modem error, " + str(ex))
            return False
        time.sleep(1)  # Esperar a que el puerto se estabilice
        return True
        
    def atCMD(self, command, exp="OK", timeout=2.0):

        if sdata.m0 is None:
            print("The modem uart is not initialized, see help")
            return False, ""

        timeout = timeout  * 1000

        while sdata.m0.any():
            sdata.m0.read()

        # Command execution Status
        cmdsts=True

        # Passthrow quotation marks
        command = command.replace("\\@", '"')

        # Enviar comando
        sdata.m0.write(command + '\r\n')
       
        if self.scmds:
            print(">> " + command)
       
        time.sleep(0.100)
       
        # Esperar respuesta
        resp = ""
        start_time = time.ticks_ms()
        
        #print("*****: " + str(timeout))
        
        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            if sdata.m0.any():
                data = sdata.m0.read().decode('utf-8')
                resp += data

                # TODO: Test: ERROR, FAIL, add: SEND OK, SEND FAIL, busy p...
                if exp == "OK" and "\r\nOK\r\n" in resp:
                    #print("*****: Brk 0")
                    break
                elif "\r\nERROR\r\n" in resp or "\r\nFAIL\r\n" in resp:
                    cmdsts=False
                    #print("*****: Brk 1")
                    break
                elif exp in resp:
                    #print("*****: Brk 2")
                    break

            time.sleep(0.02)
        
        time.sleep(0.05)
        
        if self.sresp:
            print(f"<< {resp}")

        if self._callback:
           self._callback(command, resp)
        
        return cmdsts, resp
    
    def rcvDATA(self, timeout=5.0):
        timeout = timeout  * 1000

        # Esperar respuesta
        resp = ""
        start_time = time.ticks_ms()
        
        #print("*rcv****: " + str(timeout))
        
        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            if sdata.m0.any():
                data = sdata.m0.read().decode('utf-8')
                resp += data
                start_time = time.ticks_ms() # restart if new data
                
                if"\r\nCLOSED\r\n" in resp:
                    #print("*****: Brk rcv 1")
                    break

            time.sleep(0.02)
        
        if self.sresp:
            print(f"<< data: {resp}")

        return True, resp
 
# ------ Command Implementations

    def test(self):
        sts, ret = self.atCMD("AT")
        if sts:
            lines = ret.split('\n')
            return(lines[2])
        return "Error test"

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
    
    def tcp_conn(self, host, port, keepalive=60):
        command = f'AT+CIPSTART="TCP","{host}",{port},{keepalive}'
        sts, _ = self.atCMD(command, "CONNECT", 10000)
        return sts
    
    def send_data(self, data):
        # Primero establecer longitud de datos
        length_cmd = f"AT+CIPSEND={len(data)}"
        sts, _ = self.atCMD(length_cmd, ">")
        if sts:
            # Enviar datos reales
            sts, ret = self.atCMD(data, "SEND OK")
            return ret is not sts
        return False
    
    def send_data_transparent(self, data):
        """Enviar datos en modo transparente"""
        # Primero establecer longitud
        length_cmd = f"AT+CIPSEND={len(data)}"
        sts, _ = self.atCMD(length_cmd, ">")
        if sts:
            # Enviar datos
            sdata.m0.write(data)
            sts, ret = self.atCMD("", "SEND OK") is not None
            return ret is not sts
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
    
    # MQTT CMDs
    
    def mqtt_set_config(self, broker, port=1883):
        """Configurar broker MQTT (AT+MQTTCFG)"""
        command = f'AT+MQTTCFG="{broker}",{port},120,0,0,"",""'
        return self.atCMD(command, "OK") is not None
    
    def mqtt_connect(self, client_id, username="", password=""):
        """Conectar al broker MQTT (AT+MQTTCONN)"""
        command = f'AT+MQTTCONN=0,"{client_id}",120,0,"{username}","{password}"'
        result = self.atCMD(command, "+MQTTCONN:0,0", 15000)
        
        if result and "+MQTTCONN:0,0" in result:
            self.mqtt_connected = True
            return True
        return False
    
    def mqtt_disconnect(self):
        """Desconectar de MQTT (AT+MQTTDISC)"""
        result = self.atCMD("AT+MQTTDISC=0,120", "OK")
        if result:
            self.mqtt_connected = False
            return True
        return False
    
    def mqtt_publish(self, topic, message, qos=0, retain=0):
        """Publicar mensaje MQTT (AT+MQTTPUB)"""
        # Primero establecer el topic
        topic_cmd = f'AT+MQTTPUB=0,"{topic}","{message}",{qos},{retain},120'
        return self.atCMD(topic_cmd, "OK") is not None
    
    def mqtt_subscribe(self, topic, qos=0):
        """Suscribirse a topic MQTT (AT+MQTTSUB)"""
        command = f'AT+MQTTSUB=0,"{topic}",{qos},120'
        return self.atCMD(command, "OK") is not None
    
    def mqtt_unsubscribe(self, topic):
        """Cancelar suscripción MQTT (AT+MQTTUNSUB)"""
        command = f'AT+MQTTUNSUB=0,"{topic}",120'
        return self.atCMD(command, "OK") is not None
    
    def check_messages(self):
        """Verificar mensajes MQTT recibidos"""
        messages = []
        
        # Leer todos los datos disponibles
        if sdata.m0.any():
            data = sdata.m0.read(sdata.m0.any()).decode('utf-8')
            print(f"Datos recibidos: {data}")
            
            # Procesar mensajes MQTT
            lines = data.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('+MQTTSUBRECV:'):
                    # Formato: +MQTTSUBRECV:0,topic,len,message
                    parts = line.split(',')
                    if len(parts) >= 4:
                        topic = parts[1].strip('"')
                        message_len = int(parts[2])
                        message = parts[3].strip('"')
                        messages.append((topic, message))
                        
        return messages
    
    def mqtt_get_status(self):
        """Obtener estado MQTT (AT+MQTTSTATUS)"""
        return self.atCMD("AT+MQTTSTATUS=0", "OK")
    
    def mqtt_set_clean_session(self, clean_session=1):
        """Configurar clean session (AT+MQTTCLEAN)"""
        return self.atCMD(f"AT+MQTTCLEAN=0,{clean_session}", "OK") is not None
    
    def mqtt_set_will(self, topic, message, qos=0, retain=0):
        """Configurar mensaje Will (AT+MQTTWILL)"""
        command = f'AT+MQTTWILL=0,"{topic}","{message}",{qos},{retain}'
        return self.atCMD(command, "OK") is not None
    
    def mqtt_ping(self):
        """Enviar ping MQTT (AT+MQTTPING)"""
        return self.atCMD("AT+MQTTPING=0", "OK") is not None
    
    def enable_transparent_mode(self, enable=True):
        """Habilitar/deshabilitar modo transparente"""
        mode = 1 if enable else 0
        return self.atCMD(f"AT+CIPMODE={mode}", "OK")
    

    


# -------

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
    modem = ModemManager(sctrl=False, scmds=False, sresp=True)

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
        exp="OK"
        if len(args) > 1:
            timeout = float(args[1])
        if len(args) > 2:
            exp = float(args[1])
           
        sts, resp = modem.atCMD(args[0], exp, timeout)
        if not sts:
            utls.setenv("?", "-1")

# To call out upyos
if __name__ == "__main__":
    __main__(["-f", "/local/dial.inf"])