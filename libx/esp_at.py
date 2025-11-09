# ESP-AT Modem library

from machine import UART, Pin, RTC
import time
import sdata
import utls

class ModemManager:
    def __init__(self, device="modem0"):
        
        self.device = device
        self.modem  = None
        
        if hasattr(sdata, device):
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
                print("** Reseting Modem...", end="")
        
            resetP.value(0)
            time.sleep_ms(100) # 100ms pulse
            resetP.value(1)

            time.sleep(wait) # wait to ready
            if self.sctrl:
                print(", Ready")
        except Exception as ex:
            print(", Error\nModem reset error, " + str(ex))
            return False
        return True
            
    def createUART(self, id, baud, tx, rx, device="modem0"):
        try:
            
            self.device = device
            self.modem = UART(id, baud, tx=Pin(tx), rx=Pin(rx))
            setattr(sdata, self.device, self.modem)

            if self.sctrl:
                print(f"** UART {id} created as {device}")
            
        except Exception as ex:
            print("Crerate uart error, " + str(ex))
            return False
        
        time.sleep(1)  # Esperar a que el puerto se estabilice
            
        return True
        
    def atCMD(self, command, timeout=2.0, exp="OK"):

        if self.timming: 
            self.tini = time.ticks_ms()

        if self.modem is None:
            print("The modem uart is not initialized, see help")
            return False, ""

        timeout = timeout  * 1000

        while self.modem.any():
            self.modem.read()

        # Command execution Status
        cmdsts=False

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

        expected_responses = {"OK", "SEND OK", "ERROR", "SEND FAIL", "SET OK"}

        #print(f"**** Exp {exp}")

        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            if self.modem.any():
                data = self.modem.read()
                resp += data

                if exp in expected_responses:
                    if f"\r\n{exp}\r\n" in resp:
                        if exp in {"OK", "SEND OK", "SET OK"}:
                            cmdsts = True
                        break
                elif exp in resp:
                    cmdsts = True
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
        
    def set_mode(self, mode=1):
        """Establecer modo WiFi (1=station, 2=AP, 3=both)"""
        sts, _ = self.atCMD(f"AT+CWMODE={mode}")
        return sts
        
    def wifi_connect(self, ssid, password):        
        # Conectar a WiFi
        cmd = f'AT+CWJAP="{ssid}","{password}"'
        sts, resp = self.atCMD(cmd, 15)
        return sts, resp

    def wifi_disconnect(self):
        sts, _ = self.atCMD("AT+CWQAP")
        return sts

    def wifi_status(self):
        sts, ret = self.atCMD("AT+CWSTATE?")
        if sts:
            for linea in ret.split('\n'):       
                if '+CWSTATE:' in linea:
                    return linea.split(':', 1)[1]
        else:
            return ""

    def set_ntp_server(self, en=1, tz=1, ns1="es.pool.ntp.org", ns2="es.pool.ntp.org"):
                              #AT+CIPSNTPCFG=1,1,"es.pool.ntp.org","es.pool.ntp.org"
        sts, ret = self.atCMD(f'AT+CIPSNTPCFG={en},{tz},"{ns1}","{ns2}"', 10, "+TIME_UPDATED")
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
            return rtc.datetime()
            #return sts

    def get_ip_mac(self, ip_mac):
        sts, ret = self.atCMD("AT+CIFSR")
        if sts:
            lines = ret.split('\n')
            if ip_mac.lower()=="ip":
                return(lines[1].split(",")[1])
            else:
                return(lines[2].split(",")[1])
            
        return "Error get iP/mac"
    
    # Tcp CMDs
    
    def create_conn(self, host, port, prot="TCP", keepalive=60):
        command = f'AT+CIPSTART="{prot}","{host}",{port},{keepalive}'
        sts, _ = self.atCMD(command, 10.0, "CONNECT")
        return sts
    
    def send_data(self, data):
        # Primero establecer longitud de datos
        lcmd = f"AT+CIPSEND={len(data)}"
        sts, r = self.atCMD(lcmd, 5, ">")
        if sts:
            # Enviar datos reales
            sts, ret = self.atCMD(data, 5, "SEND OK")
            return sts
        return False
    
    def send_data_transparent(self, data):
        """Enviar datos en modo transparente"""
        # Primero establecer longitud
        length_cmd = f"AT+CIPSEND={len(data)}"
        sts, _ = self.atCMD(length_cmd, 3, ">")
        if sts:
            # Enviar datos
            self.modem.write(data)
            sts, ret = self.atCMD("", 3, "SEND OK")
            return sts
        return False
    
    def close_conn(self):
        """Cerrar conexión"""
        sts, _ = self.atCMD("AT+CIPCLOSE")
        return sts
    
    def enable_multiple_connections(self, enable=True):
        """Habilitar múltiples conexiones"""
        # Todo: Astk mode 1?
        mode = 1 if enable else 0
        return self.atCMD(f"AT+CIPMUX={mode}")

# MQTT Implementation

class MqttManager(ModemManager):
    
    def __init__(self, device="modem0"):
        super().__init__(device)

        self.debug = False
        self.buffer = "" # Message buffer
        
    # MQTT CMDs

    def mqtt_conncfg(self, keepalive=0, clean_sess=1, topic="", msg="", qos=0, retain=0):
        command = f'AT+MQTTCONNCFG=0,{keepalive},{clean_sess},"{topic}","{msg}",{qos},{retain}'
        sts, _ = self.atCMD(command)
        return sts

    def mqtt_user(self, schem=1, client="", user="", passw="", cert_key_ID=0, CA_ID=0, path=""):
        command = f'AT+MQTTUSERCFG=0,{schem},"{client}","{user}","{passw}",{cert_key_ID},{CA_ID},"{path}"'
        sts, _ = self.atCMD(command)
        return sts

    def mqtt_connect(self, host="", port=1883, reconnect=0):
        command = f'AT+MQTTCONN=0,"{host}",{port},{reconnect}'
        sts, _ = self.atCMD(command, 3.0, "+MQTTCONNECTED:0")
        return sts
    
    def mqtt_pub(self, topic="", msg="", qos=0, retain=0):
        sts, _ = self.atCMD(f'AT+MQTTPUB=0,"{topic}","{msg}",{qos},{retain}')
        return sts
    
    def mqtt_sub(self, topic="", qos=0):
        sts, _ = self.atCMD(f'AT+MQTTSUB=0,"{topic}",{qos}')
        return sts
    
    def mqtt_list_subs(self):
        sts, res = self.atCMD(f'AT+MQTTSUB?')
        sl=""
        if sts:
            for l in res.split():
                if l.startswith("+MQTTSUB:0"):           
                    sl += l.split(",")[2] + "\n"
        return sl

    def mqtt_unsub(self, topic=""):
        sts, _ = self.atCMD(f'AT+MQTTUNSUB=0,"{topic}"')
        return sts

    def mqtt_clean(self):
        sts, _ = self.atCMD(f'AT+MQTTCLEAN=0')
        return sts

# ---------
    
    def parse_mqttsubrecv(self, data):
        """
        Parsea los mensajes +MQTTSUBRECV del formato:
        +MQTTSUBRECV:<LinkID>,<topic>,<data_length>,<data>
        
        Returns:
            dict con link_id, topic, data_length, data o None si no es válido
        """
        if '+MQTTSUBRECV:' not in data:
            return None
        
        try:
            # Extraer la línea que contiene +MQTTSUBRECV
            lines = data.split('\n')
            for line in lines:
                if '+MQTTSUBRECV:' in line:
                    # Formato: +MQTTSUBRECV:<LinkID>,"<topic>",<length>,<data>
                    line = line.strip()
                    parts = line.replace('+MQTTSUBRECV:', '').split(',', 3)
                    
                    if len(parts) >= 4:
                        link_id = int(parts[0])
                        topic = parts[1].strip('"')
                        data_length = int(parts[2])
                        message_data = parts[3]
                        
                        return {
                            'link_id': link_id,
                            'topic': topic,
                            'data_length': data_length,
                            'data': message_data,
                            'raw': line
                        }
        except Exception as e:
            print(f"Error parseando mensaje: {e}")
        
        return None
    
    def check_messages(self, timeout_ms=100):
        """
        Comprueba si hay mensajes MQTT recibidos
        
        Returns:
            Lista de mensajes parseados o lista vacía
        """
        messages = []
        
        # Leer datos disponibles
        if self.modem.any():
            data = self.modem.read()
            if data:
                self.buffer += data.decode('utf-8', 'ignore')
                
                # Buscar mensajes completos en el buffer
                while '+MQTTSUBRECV:' in self.buffer:
                    # Buscar el final del mensaje (normalmente \n o OK)
                    end_idx = self.buffer.find('\n', self.buffer.find('+MQTTSUBRECV:'))
                    
                    if end_idx != -1:
                        msg_section = self.buffer[:end_idx + 1]
                        parsed = self.parse_mqttsubrecv(msg_section)
                        
                        if parsed:
                            messages.append(parsed)
                            if self.debug:
                                print(f"[MQTT] Mensaje recibido:")
                                print(f"  Topic: {parsed['topic']}")
                                print(f"  Data: {parsed['data']}")
                                print(f"  Length: {parsed['data_length']}")
                        
                        # Eliminar el mensaje procesado del buffer
                        self.buffer = self.buffer[end_idx + 1:]
                    else:
                        break
        
        return messages
    
    def msgs_loop(self, callback=None):
        """
        Bucle continuo de monitoreo de mensajes MQTT
        
        Args:
            callback: Función a llamar cuando se recibe un mensaje
                     Debe aceptar un dict con el mensaje parseado
        """
        print("Starting callback MQTT message monitoring ...")
        print("Ctrl+C to stop")
        
        try:
            while True:
 
                # Thread control
                if proc.sts=="S":break
        
                if proc.sts=="H":
                    time.sleep(1)
                    continue
                
                messages = self.check_messages()
                
                for msg in messages:
                    if callback:
                        callback(msg)
                
                time.sleep_ms(10)  # Pequeña pausa para no saturar
                
        except KeyboardInterrupt:
            print("\nMonitoreo detenido")

