# ESP-AT Modem library for Espressif devices with ESP-AT firmware

from machine import UART, Pin, RTC
import time
import sdata
import utls

class ModemManager:
    def __init__(self, device="modem0"):
        
        self.phost = ""
        
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
        
    def createUART(self, id, baud, tx, rx, device="modem0", rts=7, cts=6, flow=UART.RTS|UART.CTS):

        try:

            self.device = device
            
            # With flow control for RPO4020, default
            self.modem = UART(id, baud, bits=8, parity=None, stop=1,
                                        tx=Pin(tx), rx=Pin(rx),
                                        rts=Pin(rts), cts=Pin(cts),
                                        txbuf=256, rxbuf=1024,
                                        timeout=0, timeout_char=0,
                                        flow=flow) # Important!!!

            setattr(sdata, self.device, self.modem)

            if self.sctrl:
                print(f"** UART {id} created as {device}")
            
        except Exception as ex:
            print("Crerate uart error, " + str(ex))
            return False
        
        time.sleep(1)  # Esperar a que el puerto se estabilice
            
        return True
    
    def _drain(self):
        # vacía el buffer UART
        t0 = time.time()
        while self.modem.any() and (time.time() - t0) < 0.01:
            self.modem.read()
            
    def atCMD(self, command, timeout=2.0, exp="OK"):

        if self.timming: 
            self.tini = time.ticks_ms()

        if self.modem is None:
            print("The modem uart is not initialized, see help")
            return False, ""

        timeout = timeout  * 1000

        self._drain()

        # Command execution Status
        cmdsts=False

        # Passthrow quotation marks
        command = command.replace("\\@", '"')

        # Enviar comando
        self.modem.write(command + '\r\n')
       
        if self.scmds:
            print(">> " + command)
       
        time.sleep(0.050)
       
        # Esperar respuesta
        resp = b""
        start_time = time.ticks_ms()
        
        #print("*****: " + str(timeout))

        exp_resp = {"OK", "SEND OK", "ERROR", "SEND FAIL", "SET OK"}

        #print(f"*** Exp {exp}")

        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            if self.modem.any():
                data = self.modem.read()
                #print(f"**atCMD*** << {data}")
                resp += data

                if exp in exp_resp:
                    if f"\r\n{exp}\r\n" in resp:
                        if exp in {"OK", "SEND OK", "SET OK"}:
                            #print("*** P1 OK***")
                            cmdsts = True
                            break
                elif exp in resp:
                    #print("*** P1 Other***")
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

    def clear_ipd(self, data):
        ipd_pattern = b'\r\n\r\n+IPD,' if isinstance(data, bytes) else '\r\n\r\n+IPD,'
        colon = b':' if isinstance(data, bytes) else ':'
        
        result = data
        while True:
            p_ipd = result.find(ipd_pattern)
            if p_ipd == -1:
                break
                
            p_dp = result.find(colon, p_ipd)
            if p_dp == -1:
                print("Error clear_ipd-01")
                break
                
            result = result[:p_ipd] + result[p_dp + 1:]
        
        return result

    def rcv_data(self, size=1024, encoded=True, timeout=8.0):
        
        if self.timming:
            ptini = time.ticks_ms()
        
        timeout = timeout  * 1000

        # Important, to wait !!
        #time.sleep(0.100)

        resp = b""
        start_time = time.ticks_ms()
        
        ndc=0 # No data count
        
        #print("*rcv****: " + str(timeout))
        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            if self.modem.any():
                ndc = -1
                data = self.modem.read()
                #print(f"*rcvDATA*** <<  {data}")
                
                if b"\r\nCLOSED\r\n" in data:
                    cidx = data.find(b"\r\nCLOSED\r\n")
                    if cidx > -1:
                        resp += data[:cidx]
                    #print("*****: Brk rcv 1 closed")
                    break
                else:
                    resp += data
                
                start_time = time.ticks_ms() # restart if new data
                
                if size > 0 and len(resp) >= size:
                    print(f"Warning: Size truncated")
                    #print("*****: Brk rcv 0 more...")
                    break
                
            else:
                ndc += 1
                #print("No data")
                time.sleep(0.050)
                
            time.sleep(0.010)
            if ndc > 25:
                #print("*****: Brk rcv 2")
                break
        
        #print("breaking...")
        
        if encoded:
            retResp = resp.decode('utf-8')
        else:
            retResp = resp

        retResp = self.clear_ipd(retResp)

        headers = ""
        body_ini = retResp.find("\r\n\r\n")
        if body_ini > -1:
            headers = retResp[:body_ini]
            retResp = retResp[body_ini + 4:] 

        if self.sresp:
            print(f"<< Headers: {headers}")
            print(f"<< Body: {retResp}")

        if self.timming:            
            ptfin = time.ticks_diff(time.ticks_ms(), ptini)
            print(f"## Tiempo rcv: {ptfin}ms" )
            
        return True, retResp, headers
    
    def rcv_to_file_t(self, fh, timeout=8.0):
        
        if self.timming:
            ptini = time.ticks_ms()
        
        timeout = timeout * 1000

        # Esperar respuesta
        start_time = time.ticks_ms()
        ndc = 0  # No data count
        
        hf = False
        headers = ""
        buffer = b""  # Buffer para acumular datos antes de encontrar headers
        
        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            
            if self.modem.any():
                
                data = self.modem.read()
                ndc = 1
                
                #print(f"*rcvDATA*** <<  {data}")
                
                time.sleep_ms(10)
                
                if not hf:
                    # Acumular datos mientras no se hayan encontrado los headers
                    buffer += data
                    
                    # Buscar el separador de headers en los datos acumulados
                    body_ini = buffer.find(b"\r\n\r\n")
                    
                    if body_ini > -1:
                        # Headers encontrados
                        headers = buffer[:body_ini + 4]
                        data = buffer[body_ini + 4:]  # El resto es body
                        hf = True
                        buffer = b""  # Limpiar el buffer
                        #print(f"*** Headers found!")

                        # Verificar error HTTP en headers
                        if headers.find(b"HTTP/1.1 200 OK") == -1 and headers.find(b"HTTP/") > -1:
                            # Si hay respuesta HTTP pero no es 200 OK
                            #print(f"HTTP Error in headers: {headers}")
                            # Continuar para verificar si hay error en el body también
                            return False, headers
                    else:
                        # Headers aún no completos, continuar acumulando
                        start_time = time.ticks_ms()  # Reiniciar timeout
                        continue
                
                # Procesar body solo si ya se encontraron los headers
                if hf:
                    # Escribir datos al archivo
                    try:
                        fh.write(data)
                        #print(f"Data {data}")
                    except Exception as e:
                        print(f"Error writing file - {str(e)}")
                        return False, headers
                
                start_time = time.ticks_ms()  # Reiniciar timeout si hay nuevos datos

            else:
                if ndc > 0:
                    ndc += 1
                #print(f"No data {ndc}")
                if ndc > 25:
                    break
                
                time.sleep_ms(20)
        
            time.sleep_ms(5)
        
        fh.flush()
        
        if self.timming:
            ptfin = time.ticks_diff(time.ticks_ms(), ptini)
            print(f"## Tiempo rcv: {ptfin}ms")
        
        return True, headers

    def http_to_file(self, url, filename=""):
        
        prot, _, hostport, path = url.split('/', 3)
        port = 443 if prot.lower() == "https:" else 80
        con = "SSL" if prot.lower() == "https:" else "TCP"

        tmp = hostport.split(':')
        if len(tmp) == 1:
            host = tmp[0]
        else:
            host = tmp[0]
            port = tmp[1]

        if self.phost != host:
            self.create_conn(host, port, con, keepalive=60)
        
        self.atCMD("ATE0")
        self.atCMD("AT+CIPMODE=1")
        
        if not path.startswith("/"): path = "/" + path
        
        req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\nUser-Agent: upyOS\r\nAccept: */*\r\n\r\n"
        #req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: upyOS\r\nAccept: */*\r\n\r\n"

        # Entrar en modo transparente
        self.send_passthrow()
        
        time.sleep(0.050)
        self._drain()
        time.sleep(0.050)
        self.modem.write(req.encode('utf-8'))
        time.sleep(0.050)
        sts = False
        with open(filename, 'wb') as f:
            sts, headers = self.rcv_to_file_t(f, 8)
        
        time.sleep(1)
        self.modem.write("+++")
        time.sleep(1)
        self.atCMD("AT+CIPMODE=0", 3)
        
        #if self.phost != host: 
        #    self.close_conn()
            
        self.atCMD("ATE1", 2)
        
        self.phost = host
        
        return sts

# ------ Command Implementations

    def test(self):
        sts, ret = self.atCMD("AT")
        if sts:
            lines = ret.split('\n')
            return(lines[2])
        return "Error test"
    
    def get_version(self):
        sts, ret = self.atCMD("AT+GMR")
        if sts:
            return ret.replace("\r\nOK\r\n", "").replace("AT+GMR\r\n", "")
        
    def wifi_set_mode(self, mode=1):
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

    def ping(self, host=""):
        sts, ret = self.atCMD(f'AT+PING="{host}"')
        return ret.split()[1]

    def set_ntp_server(self, en=1, tz=1, ns1="es.pool.ntp.org", ns2="es.pool.ntp.org"):
                              #AT+CIPSNTPCFG=1,1,"es.pool.ntp.org","es.pool.ntp.org"
        sts, ret = self.atCMD(f'AT+CIPSNTPCFG={en},{tz},"{ns1}","{ns2}"', 10, "+TIME_UPDATED")
        #sts, ret = self.atCMD(f'AT+CIPSNTPCFG={en},{tz},"{ns1}","{ns2}"', 10, "OK")
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
    
    def send_passthrow(self, tout=5):
        lcmd = "AT+CIPSEND"
        sts, ret = self.atCMD(lcmd, 3, ">")
        if sts:
            return sts, ret
        return False, ""
    
    def send_data(self, data, tout=5):
        lcmd = f"AT+CIPSEND={len(data)}"
        sts, ret = self.atCMD(lcmd, 3, ">")
        if sts:
            # Enviar datos
            sts, ret = self.atCMD(data, tout, "SEND OK")
            ret = self.clear_ipd(ret)
            return sts, ret
        return False, ""
    
    def send_data_transp(self, data, tout=5):
        """Send transparent mode data"""
        lcmd = f"AT+CIPSEND={len(data)}"
        sts, _ = self.atCMD(lcmd, tout, ">")
        if sts:
            # Send data
            self.modem.write(data)
            sts, ret = self.atCMD("", tout, "SEND OK")
            ret = self.clear_ipd(ret)
            return sts, ret
        return False, ""
    
    def close_conn(self):
        """Cerrar conexión"""
        sts, _ = self.atCMD("AT+CIPCLOSE")
        return sts


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

