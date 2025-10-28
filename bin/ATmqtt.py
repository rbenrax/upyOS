
# MQTT manager

from ATmodem import ModemManager
import time
import sdata
import utls
import sys

proc=None

class MqttManager(ModemManager):
    
    def __init__(self, device="modem0"):
        super().__init__(device)

        self.debug = False
        self.buffer = "" # Message buffer
        
    # MQTT CMDs

    def mqtt_conncfg(self, keepalive=0, clean_sess=1, topic="", msg="", qos=0, retain=0):
        command = f'AT+MQTTCONNCFG=0,{keepalive},{clean_sess},"{topic}","{msg}",{qos},{retain}'
        sts, _ = self.atCMD(command, 1)
        return sts

    def mqtt_user(self, schem=1, client="", user="", passw="", cert_key_ID=0, CA_ID=0, path=""):
        command = f'AT+MQTTUSERCFG=0,{schem},"{client}","{user}","{passw}",{cert_key_ID},{CA_ID},"{path}"'
        sts, _ = self.atCMD(command, 1)
        return sts

    def mqtt_connect(self, host="", port=1883, reconnect=0):
        command = f'AT+MQTTCONN=0,"{host}",{port},{reconnect}'
        sts, _ = self.atCMD(command, "+MQTTCONNECTED:0", 3.0)
        return sts
    
    def mqtt_pub(self, topic="", msg="", qos=0, retain=0):
        sts, _ = self.atCMD(f'AT+MQTTPUB=0,"{topic}","{msg}",{qos},{retain}', 1)
        return sts
    
    def mqtt_sub(self, topic="", qos=0):
        sts, resp = self.atCMD(f'AT+MQTTSUB=0,"{topic}",{qos}', 1)
        return sts
    
    def mqtt_list_subs(self):
        sts, res = self.atCMD(f'AT+MQTTSUB?', 1)
        sl=""
        if sts:
            for l in res.split():
                if l.startswith("+MQTTSUB:0"):           
                    sl += l.split(",")[2] + "\n"
        return sl

    def mqtt_unsub(self, topic=""):
        sts, _ = self.atCMD(f'AT+MQTTUNSUB=0,"{topic}"', 1)
        return sts

    def mqtt_clean(self):
        sts, _ = self.atCMD(f'AT+MQTTCLEAN=0', 1)
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



# ---------
# Callback ejemplo de uso
def on_message_received(msg):
    """Callback personalizado para procesar mensajes"""
    print(f"\n>>> Callback <<<")
    print(f"Topic: {msg['topic']}")
    print(f"Message: {msg['data']}")
    
    # Aquí puedes añadir tu lógica personalizada
    if msg['topic'] == 'casa/sotano/temp':
        try:
            temp = float(msg['data'])
            print(f"Temperatura: {temp}°C")
        except:
            pass
        
    if msg['topic'] == 'casa/sotano/hum':
        try:
            hum = float(msg['data'])
            print(f"Humedad: {hum}°C")
        except:
            pass
    
# ---------

def __main__(args):

    #TODO: add qos, reconnect and others parms

    if len(args) == 0 or "--h" in args:
        print("MQTT Library and command line utility for AT-ESP serial modem")
        print("Usage:\t First command executed connect with -h <host> [-p <port> -u <user> -P <pasword> -R <reconnect>]")
        print("\t ATmqtt <pub> -t <topic> -m <message> [-q <qos> -r <retain>]")
        print("\t ATmqtt <sub> -t <topic> [-q <qos>]")
        print("\t ATmqtt <listsub>")
        print("\t ATmqtt <unsub>")
        print("\t ATmqtt <close>")
        print("\t -l [l] listen, -v Verbose, -tm Timmings")
        return

    def parse(mod):
        try:
            if mod in args:
                i = args.index(mod)
                if i+1 < len(args):
                    return args[i + 1] if i > 0 else ""
                else:
                    print(mod + " value, not found")
                    return ""
            else:
                return ""
        except Exception as ex:
            print("ATmqtt modifier error, " + mod)
            if sdata.debug:
                sys.print_exception(ex)
            return ""

    cmd = args[0]

    host  = parse("-h")
    port  = parse("-p")
    port  = int(port) if port != "" else 1883
    user  = parse("-u")
    passw = parse("-P")
    recon = parse("-R")
    recon = 1 if recon == "1" else 0
    
    topic = parse("-t")
    messg = parse("-m")
    
    qos   = parse("-q")
    qos   = int(qos) if qos in ["1", "2"] else 0
    retain = parse("-r")
    retain = 1 if retain == "1" else 0

    mm = MqttManager() # default dev= sdata.modem0
    
    # If modem not connected
    if not mm.modem:
        print("Connecting WIFI...")
        mm.executeScript("/etc/modem.inf") # Connection script
        #mm.executeScript("/local/dial.inf")
    
    if "-v" in args:
        mm.sctrl = True
        mm.scmds = True
        mm.sresp = True
        args = [arg for arg in args if arg != "-v"]
        
    if "-tm" in args:
        mm.timming = True
        args = [arg for arg in args if arg != "-tm"]
    
    # Wifi Connection by program
    #mm.resetHW(22, 2)
    #if not mm.createUART(1, 115200, 4, 5):
    #    return
    
    #mm.wifi_connect("SSID","PASSW")
    
    #print("Test: "    + str(mm.test_modem()))
    #print("Version: " + mm.get_version())
    #print("Local IP: " + mm.get_ip_mac("ip"))
    #print("MAC: "     + mm.get_ip_mac("mac"))

    connected = utls.getenv("mqtt")
    
    if connected != "c":
        
        if not "-h" in args:
            print("-h required")
            return
        if not "-u" in args:
            print("-u required")
            return
        if not "-P" in args:
            print("-P required")
            return

        print(f"Connecting MQTT {host} ...", end="")
        mm.mqtt_user(1, sdata.sid, user, passw)
        if mm.mqtt_connect(host, port, recon):
            utls.setenv("mqtt", "c")
            print(", Connected")
        else:
            utls.setenv("mqtt", "d")
            print(", No connected")
            return

    if cmd == "pub":
        if not "-t" in args or topic == "":
            print("-t required")
            return
        if not "-m" in args or messg == "":
            print("-m required")
            return
        if mm.mqtt_pub(topic, messg, qos, retain):
            print(f"Message '{topic}': '{messg}' published")
        else:
            print(f"Publish '{topic}': '{messg}' failed")
        
    elif cmd == "sub":
        if not "-t" in args or topic == "":
            print("-t required")
            return
        if mm.mqtt_sub(topic, qos):
            print(f"Subscription '{topic}' Ok")
        else:
            print(f"Subscription '{topic}' failed")

    elif cmd == "listsub":
        # TODO: parse
        print(mm.mqtt_list_subs())
        
    elif cmd == "unsub":
        if not "-t" in args or topic == "":
            print("-t required")
            return
        if mm.mqtt_unsub(topic):
            print(f"Unsubscription '{topic}' Ok")
        else:
            print(f"Unsubscription '{topic}' failed")

    elif cmd == "close":
        mm.mqtt_clean()
        utls.setenv("mqtt", "d")
        print("MQTT closed")
    else:
       print(f"MQTT not valid subcommand {cmd}")

    if "-l" in args:
        # Option:
        print("Listening MQTT messages...")
        while True:
            
            # Thread control
            if proc.sts=="S":break

            if proc.sts=="H":
                time.sleep(1)
                continue
            
            messages = mm.check_messages()
            if messages:
                for msg in messages:
                    print(f"{msg['topic']}: {msg['data']}")
            time.sleep(0.1)

    if "-ll" in args:
        print("Listening MQTT messages...")
        # For callbach use
        mm.msgs_loop(callback=on_message_received)

