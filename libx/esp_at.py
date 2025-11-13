# ESP-AT Modem library for Espressif devices with ESP-AT firmware

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
    
    def _drain(self):
        # vacía el buffer UART
        t0 = time.time()
        while self.modem.any() and (time.time() - t0) < 0.1:
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

    def rcvDATA(self, size=1024, encoded=True, timeout=8.0):
        
        if self.timming:
            ptini = time.ticks_ms()
        
        timeout = timeout  * 1000

        # Esperar respuesta
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
                    if cidx > 0:
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
        body_ini = retResp.index("\r\n\r\n")
        if body_ini > 0:
            headers = retResp[:body_ini]
            retResp = retResp[body_ini + 4:] 

        if self.sresp:
            print(f"<< Headers: {headers}")
            print(f"<< Body: {retResp}")

        

        if self.timming:            
            ptfin = time.ticks_diff(time.ticks_ms(), ptini)
            print(f"## Tiempo rcv: {ptfin}ms" )

        return True, retResp, headers
    
    def rcvDATA_tofile(self, fh, timeout=8.0):

        """
        Recibe datos del módem ESP-AT y guarda el payload en el fichero `fh`.
        - Detecta y guarda las cabeceras HTTP (antes del primer \r\n\r\n).
        - Procesa y elimina las cabeceras +IPD,<len>: incluso si llegan fragmentadas.
        - Escribe al fichero solo los datos reales del payload.
        - Usa un buffer temporal muy pequeño para ahorrar memoria.
        Devuelve (success: bool, result: dict)
        result contiene:
            'written' -> bytes escritos en total
            'headers' -> cadena con las cabeceras (si las hay)
            'errors'  -> lista de errores
        """
        import time

        start_ms = time.ticks_ms()
        timeout_ms = int(timeout * 1000)

        buf = bytearray()
        total_written = 0
        errors = []
        ndc = 0
        headers = ""
        headers_found = False

        ipd_tag = b'+IPD,'
        closed_marker = b'\r\nCLOSED\r\n'

        while time.ticks_diff(time.ticks_ms(), start_ms) < timeout_ms:
            if self.modem.any():
                ndc = -1
                chunk = self.modem.read()
                if not chunk:
                    time.sleep(0.01)
                    continue

                buf.extend(chunk)

                # Detectar cabeceras HTTP si no se han detectado todavía
                if not headers_found:
                    sep = buf.find(b'\r\n\r\n')
                    if sep != -1:
                        try:
                            headers = buf[:sep].decode('utf-8', 'ignore')
                        except Exception:
                            headers = "<decode_error>"
                        buf = buf[sep + 4:]  # eliminar cabeceras del buffer
                        headers_found = True

                # Detectar fin de conexión
                ci = buf.find(closed_marker)
                if ci != -1:
                    buf = buf[:ci]

                # Procesar posibles bloques +IPD
                while True:
                    p = buf.find(ipd_tag)
                    if p == -1:
                        # mantener pequeño el buffer
                        if len(buf) > 64:
                            buf = buf[-16:]
                        break

                    colon = buf.find(b':', p + len(ipd_tag))
                    if colon == -1:
                        if p > 0:
                            buf = buf[p:]
                        break

                    # Extraer tamaño del payload
                    num_field = buf[p + len(ipd_tag):colon]
                    try:
                        n = int(num_field)
                    except Exception:
                        errors.append("bad length field: %r" % num_field)
                        buf = buf[colon + 1:]
                        continue

                    payload_start = colon + 1
                    available = len(buf) - payload_start

                    if available >= n:
                        # Tenemos el bloque completo
                        payload = buf[payload_start:payload_start + n]
                        try:
                            fh.write(payload)
                            try:
                                fh.flush()
                            except:
                                pass
                            total_written += n
                        except Exception as e:
                            errors.append("file write error: %s" % str(e))
                            return False, {
                                'written': total_written,
                                'headers': headers,
                                'errors': errors
                            }

                        buf = buf[payload_start + n:]  # eliminar bloque procesado
                        continue
                    else:
                        # payload incompleto, esperar más datos
                        if p > 0:
                            buf = buf[p:]
                        break

                # reiniciar timeout si hay datos
                start_ms = time.ticks_ms()

                # si detectamos CLOSED y buffer vacío, salir
                if ci != -1 and len(buf) == 0:
                    break

            else:
                ndc += 1
                time.sleep(0.05)

            if ndc > 25:
                break

            time.sleep(0.005)

        # Si quedan restos en buffer
        if len(buf) > 0:
            if buf.find(ipd_tag) != -1:
                errors.append("incomplete IPD frame left in buffer (%d bytes)" % len(buf))
            elif any(b not in (0x0d, 0x0a, 0x00) for b in buf):
                errors.append("trailing non-IPD data (%d bytes) discarded" % len(buf))

        success = (len(errors) == 0)
        return success, {
            'written': total_written,
            'headers': headers,
            'errors': errors
        }


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
        length_cmd = f"AT+CIPSEND={len(data)}"
        sts, _ = self.atCMD(length_cmd, tout, ">")
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

