# MQTT manager - MicroPython Simple MQTT version

from umqtt.simple import MQTTClient
import time
import sdata
import utls
import sys

proc = None

class MqttManager:
    
    def __init__(self, client_id="", server="", port=0, user="", password="", ssl=False, ssl_params={}):
        self.client_id = client_id
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.ssl = ssl
        self.ssl_params = ssl_params
        
        self.client = None
        self.debug = sdata.debug
        self.is_connected = False
        
        # Callback para mensajes recibidos
        self.message_callback = on_message_received
        
    def mqtt_connect(self, host="", port=1883, reconnect=0):
        """
        Conecta al broker MQTT
        """
        try:
            self.server = host if host else self.server
            self.port = port if port else self.port
            
            # Crear cliente MQTT
            self.client = MQTTClient(
                self.client_id,
                self.server,
                port=self.port,
                user=self.user,
                password=self.password,
                keepalive=60,
                ssl=self.ssl,
                ssl_params=self.ssl_params
            )
            
            # Configurar callback si existe
            if self.message_callback:
                self.client.set_callback(self._internal_callback)
            
            # Conectar
            if self.client.connect(clean_session=True) == 0:
                self.is_connected = True
                if self.debug:
                    print(f"[MQTT] Connected to {self.server}:{self.port}")
            else:
                self.is_connected = False
                if self.debug:
                    print(f"[MQTT] Not Connected to {self.server}:{self.port}")
            
            return self.is_connected
            
        except Exception as e:
            if self.debug:
                print(f"[MQTT] Connection error: {e}")
            self.is_connected = False
            return False
    
    def mqtt_pub(self, topic="", data="", qos=0, retain=0):
        """
        Publica mensaje MQTT
        """
        if not self.is_connected or not self.client:
            if self.debug:
                print("[MQTT] Not connected")
            return False
        
        try:
            # umqtt.simple solo soporta qos=0
            self.client.publish(topic, data, retain=retain, qos=0)
            return True
        except Exception as e:
            if self.debug:
                print(f"[MQTT] Publish error: {e}")
            return False
    
    def mqtt_sub(self, topic="", qos=0):
        """
        Suscribe a un topic MQTT
        """
        if not self.is_connected or not self.client:
            if self.debug:
                print("[MQTT] Not connected")
            return False
        
        try:
            # umqtt.simple solo soporta qos=0
            self.client.subscribe(topic)
            
            if self.debug:
                print(f"[MQTT] Subscribed to: {topic}")
            
            return True
        except Exception as e:
            if self.debug:
                print(f"[MQTT] Subscribe error: {e}")
            return False
    
    def mqtt_list_subs(self):
        """
        Lista topics suscritos, Not implemented en library
        """
        return
    
    def mqtt_unsub(self, topic=""):
        """
        Cancela suscripción a topic
        """
        if not self.is_connected or not self.client:
            if self.debug:
                print("[MQTT] Not connected")
            return False
        
        try:
            self.client.unsubscribe(topic)
               
            if self.debug:
                print(f"[MQTT] Unsubscribed from: {topic}")
            
            return True
        except Exception as e:
            if self.debug:
                print(f"[MQTT] Unsubscribe error: {e}")
            return False

    def mqtt_clean(self):
        """
        Limpia conexión MQTT
        """
        try:
            if self.client:
                self.client.disconnect()
            self.is_connected = False
            return True
        except Exception as e:
            if self.debug:
                print(f"[MQTT] Clean error: {e}")
            return False

# ---------
# Gestión de mensajes - Adaptado para umqtt.simple
    
    def set_callback(self, callback):
        """
        Establece callback para mensajes recibidos
        """
        self.message_callback = callback
        if self.client and self.is_connected:
            self.client.set_callback(self._internal_callback)
    
    def _internal_callback(self, topic, message):
        """
        Callback interno que procesa mensajes y llama al callback del usuario
        """
        if self.message_callback:
            # Crear estructura similar a la versión ASP-AT
            msg_dict = {
                'link_id': 0,
                'topic': topic.decode('utf-8') if isinstance(topic, bytes) else topic,
                'data_length': len(message),
                'data': message.decode('utf-8') if isinstance(message, bytes) else message,
                'raw': f"+MQTTSUBRECV:0,\"{topic}\",{len(message)},{message}"
            }
            self.message_callback(msg_dict)
    
    def check_messages(self, timeout_ms=100):
        """
        Comprueba si hay mensajes MQTT recibidos (no bloqueante)
        """
        messages = []
        
        if self.is_connected and self.client:
            try:
                # Verificar si hay mensajes (no bloqueante)
                self.client.check_msg()
                # Los mensajes se manejan via callback automáticamente
            except Exception as e:
                if self.debug:
                    print(f"[MQTT] Check messages error: {e}")
        
        return messages  # En esta implementación, los mensajes van por callback
    
    def wait_msg(self, timeout=None):
        """
        Espera mensajes (bloqueante)
        """
        if self.is_connected and self.client:
            try:
                self.client.wait_msg()
                return True
            except Exception as e:
                if self.debug:
                    print(f"[MQTT] Wait message error: {e}")
                return False
        return False

    def msgs_loop(self, callback=None):
        """
        Bucle continuo de monitoreo de mensajes MQTT
        """
        if callback:
            self.set_callback(callback)
            
        print("Starting callback MQTT message monitoring ...")
        print("Ctrl+C to stop")
        
        try:
            while True:
                # Thread control
                if proc and proc.sts == "S": 
                    break
        
                if proc and proc.sts == "H":
                    time.sleep(1)
                    continue
                
                # Verificar mensajes
                self.check_messages()
                
                time.sleep_ms(10)  # Pequeña pausa para no saturar
                
        except KeyboardInterrupt:
            print("\nMonitoreo detenido")
        except Exception as e:
            print(f"\nError en bucle: {e}")

# ---------
# Callback ejemplo de uso (mantenido igual)
def on_message_received(msg):
    """Callback personalizado para procesar mensajes"""
    #print(f"\n>>> Callback <<<")
    #print(f"Topic: {msg['topic']}")
    #print(f"Message: {msg['data']}")

    print(f"'{msg['topic']}': {msg['data']}")
    
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
            print(f"Humedad: {hum}%")
        except:
            pass
    
# ---------

def __main__(args):
    """
    Función principal - Mantenida casi idéntica para compatibilidad
    """

    if len(args) == 0 or "--h" in args:
        print("MQTT Library and command line utility - MicroPython Simple MQTT")
        print("Usage:\t First command executed connect with -h <host> [-p <port> -u <user> -P <pasword> -R <reconnect>]")
        print("\t ATmqtt <pub> -t <topic> -m <message> [-q <qos> -r <retain>]")
        print("\t ATmqtt <sub> -t <topic> [-q <qos>]")
        print("\t ATmqtt <listsub> not implemented")
        print("\t ATmqtt <unsub>")
        print("\t ATmqtt <close>")
        print("\t -l[l] listen")
        return

    def parse(mod):
        try:
            if mod in args:
                i = args.index(mod)
                return args[i + 1] if i + 1 < len(args) else ""
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

    # Crear instancia MQTT
    mm = MqttManager(client_id="mqtt-esp32", server=host, port=port, user=user, password=passw)
    
    if not "-h" in args:
        print("-h required")
        return

    print(f"Connecting MQTT...")
    
    # Conectar
    if mm.mqtt_connect(host, port, recon):
        print("Connected")
    else:
        print("No connected")
        return

    if cmd == "pub":
        if not "-t" in args or topic == "":
            print("-t required")
            return
        if not "-m" in args or messg == "":
            print("-m required")
            return
        success = mm.mqtt_pub(topic, messg, qos, retain)
        if success:
            print("Message published")
        else:
            print("Publish failed")
        
    elif cmd == "sub":
        if not "-t" in args or topic == "":
            print("-t required")
            return
        success = mm.mqtt_sub(topic, qos)
        if success:
            print(f"Subscribed to {topic}")
        else:
            print("Subscribe failed")
        
    elif cmd == "listsub":
        print("Not implemented in umqtt simple library")
        
    elif cmd == "unsub":
        if not "-t" in args or topic == "":
            print("-t required")
            return
        success = mm.mqtt_unsub(topic)
        if success:
            print(f"Unsubscribed from {topic}")
        else:
            print("Unsubscribe failed")

    elif cmd == "close":
        mm.mqtt_clean()
        print("MQTT closed")

    # Opciones de escucha
    if "-l" in args:
        print("Listening MQTT messages...")
        #mm.set_callback(on_message_received)
        while True:
            # Thread control
            if proc and proc.sts == "S": 
                break

            if proc and proc.sts == "H":
                time.sleep(1)
                continue
            
            messages = mm.check_messages()
            time.sleep(0.1)
