# ESP-AT Modem library for Espressif devices with ESP-AT firmware

from machine import UART, Pin, RTC
import time
import sdata
import utls
import sys
import gc

proc = None

class ModemManager:
    def __init__(self, device="modem0"):
        
        self.device = device
        self.modem  = None
        
        if hasattr(sdata, device):
            self.modem = getattr(sdata, device)
        
        self.sctrl = False # Print ctrl messages
        self.scmds = False # Print cmds
        self.sresp = False # Print resp
        
        self.timing = False
        self.tini=0
        
        self._callback = None
        
        self.tcp_conn = False # TCP Connected?
        
    def setCallBack(self, callback): # add callback
        self._callback = callback

    def resetHW(self, pin, wait=2):
        try:
            resetP = Pin(pin, Pin.OUT, value=1)  # HIGH default

            if self.sctrl:
                print("** Resetting Modem...", end="")
        
            resetP.value(0)
            time.sleep_ms(100) # 100ms pulse
            resetP.value(1)

            self.tcp_conn = False

            time.sleep(wait) # wait for ready
            if self.sctrl:
                print(", Ready")
        except Exception as ex:
            print(", Error\nModem reset error, " + str(ex))
            return False
        return True
    
    def createUART(self, id, baud, tx, rx, device="modem0",
                   rts=7, cts=6, txbuf=256, rxbuf=1024,
                   timeout=0, timeout_char=0, flow_type="rc"):

        try:

            self.device = device
            
            if rts==0 or cts==0 or flow_type == "off":
                self.modem = UART(id, baud, bits=8, parity=None, stop=1,
                                        txbuf=txbuf, rxbuf=rxbuf,
                                        timeout=timeout, timeout_char=timeout_char)
            else:
                # Flow control enabled for RPO4020, default
                flow=UART.RTS|UART.CTS
                if flow_type == "r":   
                    flow=UART.RTS
                elif flow_type == "c":
                    flow=UART.CTS
                
                self.modem = UART(id, baud, bits=8, parity=None, stop=1,
                                        tx=Pin(tx), rx=Pin(rx),
                                        rts=Pin(rts), cts=Pin(cts),
                                        txbuf=txbuf, rxbuf=rxbuf,
                                        timeout=timeout, timeout_char=timeout_char,
                                        flow=flow) # Important!!!

            setattr(sdata, self.device, self.modem)

            time.sleep(2)

            if self.sctrl:
                print(f"UART {id} created as {device}")
            
        except Exception as ex:
            print("UART creation error, " + str(ex))
            sys.print_exception(ex)
            return False
        
        time.sleep(1)  # Wait for the port to stabilize
            
        return True
    
    def _drain(self):
        # empty UART buffer
        t0 = time.ticks_ms()
        while self.modem.any() and time.ticks_diff(time.ticks_ms(), t0) < 50:
            self.modem.read(2048)
            
    def atCMD(self, command, timeout=2.0, exp="OK"):

        if self.timing: 
            self.tini = time.ticks_ms()

        if self.modem is None:
            print("The modem UART is not initialized, see help")
            return False, ""

        timeout = timeout  * 1000

        self._drain()

        # Command execution Status
        cmdsts=False

        # Passthrow quotation marks
        #command = command.replace("\\@", '"')

        # Send command
        self.modem.write(command + '\r\n')
       
        if self.scmds:
            print(">> " + command)
       
        time.sleep(0.050)
       
        # Wait for response
        resp = b""
        start_time = time.ticks_ms()
        
        #print("*****: " + str(timeout))

        exp_resp = {"OK", "SEND OK", "ERROR", "SEND FAIL", "SET OK"}

        #print(f"*** Exp {exp}")

        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            if self.modem.any():
                data = self.modem.read(2048)
                #print(f"**atCMD*** << {data}")
                resp += data

                if exp in exp_resp:
                    if f"\r\n{exp}\r\n" in resp or resp.endswith(f"\r\n{exp}\r\n") or resp == f"{exp}\r\n":
                        if exp in {"OK", "SEND OK", "SET OK"}:
                            cmdsts = True
                            break
                elif exp.encode('utf-8') in resp:
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
            
        if self.timing:            
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

    def rcv_data(self, size=1024, encoded=True, timeout=15.0):
        
        if not self.tcp_conn:
            print("rcv_data: TCP Not connected")
            return False, "", ""
        
        if self.timing:
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
                ndc = 1
                data = self.modem.read(2048)
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
                if ndc > 0:
                    ndc += 1
                    #print(f"No data {ndc}")
                if ndc > 25:
                    break
                
                time.sleep(0.050)
                
            time.sleep(0.010)
        
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
            
            # remove +IPD
            if "\r\n+IPD," in headers:
                sep = headers.find(":")
                if sep != -1:
                    headers = headers[sep + 1:]
            
            retResp = retResp[body_ini + 4:] 

        if self.sresp:
            print(f"<< Headers: {headers}")
            print(f"<< Body: {retResp}")

        if self.timing:            
            ptfin = time.ticks_diff(time.ticks_ms(), ptini)
            print(f"## Rcv time: {ptfin}ms" )
            
        return True, retResp, headers
    
    def rcv_to_file_t(self, fh, timeout=15, msz=0):
        
        if not self.tcp_conn:
            print("rcv_to_file_t: TCP Not connected")
            return False, ""
        
        if self.timing:
            ptini = time.ticks_ms()
        
        timeout = timeout * 1000

        # Wait for response
        start_time = time.ticks_ms()
        ndc = 0  # No data count
        
        hf = False
        headers = ""
        buffer = b""  # Buffer to accumulate data before finding headers
        rcvd_body = 0
        gc.collect()
        while time.ticks_diff(time.ticks_ms(), start_time) < timeout:
            
            if self.modem.any():
                
                data = self.modem.read(2048)
                ndc = 1
                gc.collect()

                if not hf:
                    # Accumulate data while headers are not found
                    if len(buffer) + len(data) > 4096:
                        # Force header end if buffer too large to prevent MemoryError
                        hf = True
                        fh.write(buffer)
                        rcvd_body += len(buffer)
                        buffer = b""
                    else:
                        buffer += data
                        # Find header separator in accumulated data
                        body_ini = buffer.find(b"\r\n\r\n")
                        
                        if body_ini > -1:
                            # Headers found
                            headers = buffer[:body_ini + 4]
                            data = buffer[body_ini + 4:]  # The rest is body
                            hf = True
                            buffer = b""  # Clear buffer

                            # Verificar error HTTP en headers
                            if headers.find(b"HTTP/1.1 200 OK") == -1 and headers.find(b"HTTP/") > -1:
                                return False, headers
                        else:
                            # Headers not complete yet, continue accumulating
                            start_time = time.ticks_ms()  # Restart timeout
                            continue
                
                # Process body only if headers already found
                if hf:
                    # Write data to file
                    try:
                        if msz > 0:
                            rem = msz - rcvd_body
                            if len(data) > rem:
                                data = data[:rem]
                                fh.write(data)
                                rcvd_body += len(data)
                                break
                        
                        fh.write(data)
                        rcvd_body += len(data)
                        
                        if msz > 0 and rcvd_body >= msz:
                            break
                            
                    except Exception as e:
                        print(f"Error writing file - {str(e)}")
                        return False, headers
                
                start_time = time.ticks_ms()  # Restart timeout if new data

            else:
                if ndc > 0:
                    ndc += 1
                #print(f"No data {ndc}")
                if ndc > 100:
                    break
                
                time.sleep_ms(25)
        
            time.sleep_ms(5)
        
        fh.flush()
        
        if ndc == 0:
            print(f"Error: Timeout {timeout/1000}s reached with no data")
            return False, headers

        if msz > 0 and rcvd_body < msz:
            print(f"Error: Incomplete download. Expected {msz}, got {rcvd_body}")
            return False, headers
        
        if self.timing:
            ptfin = time.ticks_diff(time.ticks_ms(), ptini)
            print(f"## Rcv time: {ptfin}ms")
        
        return True, headers

    def http_get_to_file_t(self, url, filename="", tout=15, sz=0):
        
        if not self.tcp_conn:
            print("http_get_to_file_t: TCP Not connected")
            return False
        
        parts = url.split('/')
        if len(parts) < 4:
             # Handle http://host or http://host:port
             hostport = parts[2] if len(parts) > 2 else url
             path = "/"
        else:
             hostport = parts[2]
             path = "/" + "/".join(parts[3:])

        tmp = hostport.split(':')
        host = tmp[0]
        
        if not path.startswith("/"): path = "/" + path
        
        req = (f"GET {path} HTTP/1.1\r\n"
               f"Host: {host}\r\n"
               f"User-Agent: upyOS\r\n"
               f"Accept: */*\r\n"
               f"\r\n")
        
        if self.scmds:
            print(req)
        
        self._drain()
        gc.collect()
        self.modem.write(req.encode('utf-8'))
        sts = False
        with open(filename, 'wb') as f:
            sts, headers = self.rcv_to_file_t(f, tout, sz)
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
        """Set WiFi mode (1=station, 2=AP, 3=both)"""
        sts, _ = self.atCMD(f"AT+CWMODE={mode}")
        return sts
        
    def wifi_connect(self, ssid, password, tout=10):
        cmd = f'AT+CWJAP="{ssid}","{password}"'
        sts, resp = self.atCMD(cmd, tout)
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

    def set_ntp_server(self, en=1, tz=1, ns1="es.pool.ntp.org", ns2="es.pool.ntp.org", tout=10):
                              #AT+CIPSNTPCFG=1,1,"es.pool.ntp.org","es.pool.ntp.org"
        sts, ret = self.atCMD(f'AT+CIPSNTPCFG={en},{tz},"{ns1}","{ns2}"', tout, "+TIME_UPDATED")
        #sts, ret = self.atCMD(f'AT+CIPSNTPCFG={en},{tz},"{ns1}","{ns2}"', tout, "OK")
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

            # Dictionaries to translate abbreviations
            dias_semana = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5, "Sat": 6, "Sun": 7}
            meses = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                     "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

            # Split string by spaces and clean double gaps
            partes = fecha_str.split()
            # Typical result: ['Thu', 'Jan', '1', '00:00:07', '1970']

            dia_semana_str, mes_str, dia_str, hora_str, anio_str = partes

            # Decompose time
            hora, minuto, segundo = [int(x) for x in hora_str.split(":")]

            # Create tuple expected by RTC
            fecha_rtc = (
                int(anio_str),          # Year
                meses[mes_str],         # Month
                int(dia_str),           # Day
                dias_semana[dia_semana_str],  # Day of week (1=Monday ... 7=Sunday)
                hora,                   # Hour
                minuto,                 # Minute
                segundo,                # Second
                0                       # Subsegundos
            )

            # Configure RTC
            rtc = RTC()
            rtc.datetime(fecha_rtc)
            return rtc.datetime()
            #return sts

    def get_ip_mac(self, ip_mac):
        sts, ret = self.atCMD("AT+CIFSR")
        if sts:
            for line in ret.split('\n'):
                if ip_mac.lower() == "ip" and "STAIP" in line:
                    try:
                        return line.split('"')[1]
                    except:
                        pass
                if ip_mac.lower() == "mac" and "STAMAC" in line:
                    try:
                        return line.split('"')[1]
                    except:
                        pass
            
            # Fallback if specific tags not found
            lines = [l for l in ret.split('\n') if l.strip()]
            try:
                if ip_mac.lower() == "ip":
                    return lines[1].split(',')[1].strip('"')
                else:
                    return lines[2].split(',')[1].strip('"')
            except:
                pass
            
        return "Error get IP/mac"
    
    # Tcp CMDs
    def create_url_conn(self, url, keepalive=60, tout=10.0):
        prot, _, hostport, path = url.split('/', 3)
        port = 443 if prot.lower() == "https:" else 80
        ct = "SSL" if prot.lower() == "https:" else "TCP"
        
        tmp = hostport.split(':')
        if len(tmp) == 1:
            host = tmp[0]
        else:
            host = tmp[0]
            port = tmp[1]
        
        return self.create_conn(host, port, ct, keepalive, tout)
    
    def create_conn(self, host, port, ct="TCP", keepalive=60, tout=10.0):
        
        if ct == "SSL":
           _, _ = self.atCMD(f'AT+CIPSSLCSNI="{host}"') 
        
        command = f'AT+CIPSTART="{ct}","{host}",{port},{keepalive}'
        sts, _ = self.atCMD(command, tout, "CONNECT")
        
        if sts:
            self.tcp_conn = True
        else:
            self.tcp_conn = False
            
        return sts
    
    def send_passthrough(self, tout=3):
        lcmd = "AT+CIPSEND"
        sts, ret = self.atCMD(lcmd, tout, ">")
        if sts:
            return sts, ret
        return False, ""
    
    def send_data(self, data, tout=3):
        
        if not self.tcp_conn:
            print("send_data: TCP Not connected")
            return False, ""
        
        lcmd = f"AT+CIPSEND={len(data)}"
        sts, ret = self.atCMD(lcmd, tout, ">")
        if sts:
            # Send data
            sts, ret = self.atCMD(data, tout, "SEND OK")
            #ret = self.clear_ipd(ret)
            return sts, ret
        return False, ""
    
    def send_data_t(self, data, tout=5):
 
        if not self.tcp_conn:
            print("send_data_t: TCP Not connected")
            return False, ""
 
        lcmd = f"AT+CIPSEND={len(data)}"
        sts, _ = self.atCMD(lcmd, tout, ">")
        if sts:
            # Send data
            self.modem.write(data)
            sts, ret = self.atCMD("", tout, "SEND OK")
            #ret = self.clear_ipd(ret)
            return sts, ret
        return False, ""
    
    def close_conn(self):
        """Close connecting"""
        sts, _ = self.atCMD("AT+CIPCLOSE")
        self.tcp_conn = False
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
        Parses +MQTTSUBRECV messages of format:
        +MQTTSUBRECV:<LinkID>,<topic>,<data_length>,<data>
        
        Returns:
            dict with link_id, topic, data_length, data or None if not valid
        """
        if '+MQTTSUBRECV:' not in data:
            return None
        
        try:
            # Extract line containing +MQTTSUBRECV
            lines = data.split('\n')
            for line in lines:
                if '+MQTTSUBRECV:' in line:
                    # Format: +MQTTSUBRECV:<LinkID>,"<topic>",<length>,<data>
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
            print(f"Error parsing message: {e}")
        
        return None
    
    def check_messages(self, timeout_ms=100):
        """
        Checks if MQTT messages received
        
        Returns:
            List of parsed messages or empty list
        """
        messages = []
        
        # Read available data
        if self.modem.any():
            data = self.modem.read(2048)
            if data:
                self.buffer += data.decode('utf-8', 'ignore')
                
                # Find complete messages in buffer
                while '+MQTTSUBRECV:' in self.buffer:
                    # Find message end (usually \n or OK)
                    end_idx = self.buffer.find('\n', self.buffer.find('+MQTTSUBRECV:'))
                    
                    if end_idx != -1:
                        msg_section = self.buffer[:end_idx + 1]
                        parsed = self.parse_mqttsubrecv(msg_section)
                        
                        if parsed:
                            messages.append(parsed)
                            if self.debug:
                                print(f"[MQTT] Message received:")
                                print(f"  Topic: {parsed['topic']}")
                                print(f"  Data: {parsed['data']}")
                                print(f"  Length: {parsed['data_length']}")
                        
                        # Remove processed message from buffer
                        self.buffer = self.buffer[end_idx + 1:]
                    else:
                        break
        
        return messages
    
    def msgs_loop(self, callback=None):
        """
        Continuous monitoring loop for MQTT messages
        
        Args:
            callback: Function to call when a message is received
                      Must accept a dict with the parsed message
        """
        print("Starting callback MQTT message monitoring ...")
        print("Ctrl+C to stop")
        
        try:
            while True:
 
                # Thread control
                if proc and proc.sts=="S":break
        
                if proc and proc.sts=="H":
                    time.sleep(1)
                    continue
                
                messages = self.check_messages()
                
                for msg in messages:
                    if callback:
                        callback(msg)
                
                time.sleep_ms(10)  # Small pause to avoid saturation
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped")

