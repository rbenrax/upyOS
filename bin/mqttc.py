# MQTT manager - MicroPython Robust MQTT version

from umqtt.robust import MQTTClient
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
        
        if not hasattr(sdata, "mqtt_subscriptions"):
            sdata.mqtt_subscriptions = set()
        self.subscriptions = sdata.mqtt_subscriptions
        
        self.client = None
        self.debug = sdata.debug
        self.is_connected = False
        
        # Callback para mensajes recibidos
        self.message_callback = None
        
    def mqtt_connect(self, host="", port=1883, reconnect=True):
        """
        Conecta al broker MQTT
        """
        try:
            self.server = host if host else self.server
            self.port = port if port else self.port
            
            # Crear cliente MQTT robust
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
            
            # Conectar - MQTTClient robust maneja reconexiones automáticamente
            self.client.connect(clean_session=False)
            
            # CRÍTICO: Marcar como conectado
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"MQTT Connection error: {e}")
            self.is_connected = False
            return False
    
    def mqtt_pub(self, topic="", data="", qos=0, retain=0):
        try:
            # umqtt.robust soporta mejor el manejo de errores en publicación
            self.client.publish(topic, data, retain=retain, qos=qos)
            return True
        except Exception as e:
            print(f"MQTT Publish error: {e}")
            # El cliente robust intentará reconectar automáticamente
            return False
    
    def mqtt_sub(self, topic="", qos=0):
        try:
            self.client.subscribe(topic, qos=qos)
            self.subscriptions.add(topic)
            return True
        except Exception as e:
            print(f"MQTT Subscribe error: {e}")
            return False
    
    def mqtt_list_subs(self):
        """
        Lista topics suscritos, Not implemented en library
        """
        return list(self.subscriptions)
    
    def mqtt_unsub(self, topic=""):
        try:
            # Protocolo MQTT UNSUBSCRIBE = 0xA2
            pkt = bytearray(b"\xA2\0\0\0")
            pkt_id = 1  # ID fijo para simplicidad
            pkt[1] = 2 + len(topic) + 2  # longitud variable
            pkt[2] = pkt_id >> 8
            pkt[3] = pkt_id & 0xFF
            # topic
            pkt += bytearray(len(topic).to_bytes(2, 'big'))
            pkt += topic
            self.client.sock.write(pkt)
            # No hay confirmación en esta implementación mínima
        
            if topic in self.subscriptions:
                self.subscriptions.remove(topic)

        except Exception as e:
            print(f"MQTT Unsubscribe error: {e}")
            return False

    def mqtt_clean(self):
        """
        Limpia conexión MQTT
        """
        try:
            if self.client:
                self.client.disconnect()
            self.is_connected = False
            if hasattr(sdata, "mqtt_subscriptions"):
                del sdata.mqtt_subscriptions
            return True
        except Exception as e:
            print(f"MQTT Clean error: {e}")
            return False

    def ping(self):
        """
        Verifica la conexión con el broker
        """
        try:
            if self.client:
                self.client.ping()
                return True
        except Exception as e:
            print(f"MQTT Ping error: {e}")
            return False
        return False

# ---------
# Gestión de mensajes - Adaptado para umqtt.robust
    
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
                # wait_msg con timeout 0 es no bloqueante en umqtt.robust
                self.client.check_msg()
                # Los mensajes se manejan via callback automáticamente
            except Exception as e:
                if self.debug:
                    print(f"MQTT Check messages error: {e}")
        
        return messages  # En esta implementación, los mensajes van por callback
    
    def wait_for_message(self, timeout=None):
        """
        Espera mensajes (bloqueante) con manejo robusto
        """
        if self.is_connected and self.client:
            try:
                if timeout is not None:
                    # wait_msg con timeout en segundos
                    self.client.wait_msg()
                else:
                    self.client.wait_msg()
                return True
            except Exception as e:
                if self.debug:
                    print(f"MQTT Wait message error: {e}")
                return False
        return False

    def msgs_loop(self, callback=None):
        """
        Bucle continuo de monitoreo de mensajes MQTT con reconexión automática
        """
        if callback:
            self.set_callback(callback)
            
        print("Starting robust MQTT message monitoring ...")
        print("Ctrl+C to stop")
        
        try:
            while True:
                # Thread control
                if proc and proc.sts == "S": 
                    break
        
                if proc and proc.sts == "H":
                    time.sleep(1)
                    continue
                
                # Verificar mensajes - el cliente robust maneja reconexiones
                try:
                    self.check_messages()
                except Exception as e:
                    print(f"Error checking messages: {e}")
                    # El cliente robust debería intentar reconectar automáticamente
                
                time.sleep_ms(100)  # Pausa un poco más larga para eficiencia
                
        except KeyboardInterrupt:
            print("\nstopped monitoring")
        except Exception as e:
            print(f"\nLoop error: {e}")

# ---------
# Callback ejemplo de uso
def on_message_received(msg):
    """Callback personalizado para procesar mensajes"""
    print(f"{msg['topic']}: {msg['data']}")
    
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
    Función principal - Delegando persistencia a sdata
    """

    if len(args) == 0 or "--h" in args:
        print("MQTT Library and command line utility - MicroPython Robust MQTT")
        print("Usage:\t Connect with -h <host> [-p <port> -R <reconnect>]")
        print("\t ATmqtt <pub> -t <topic> -m <message> [-q <qos> -r <retain>]")
        print("\t ATmqtt <sub> -t <topic> [-q <qos>]")
        print("\t ATmqtt <listsub>")
        print("\t ATmqtt <unsub> -t <topic>")
        print("\t ATmqtt <ping> - check connection")
        print("\t ATmqtt <close>")
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
            if mm.debug:
                sys.print_exception(ex)
            return ""

    cmd = args[0]

    host  = parse("-h")
    port  = parse("-p")
    port  = int(port) if port != "" else 1883
    
    user  = parse("-u")
    passw = parse("-P")
    recon = parse("-R")
    recon = recon.lower() == "true" or recon == "1"
    
    topic = parse("-t")
    messg = parse("-m")
    
    qos   = parse("-q")
    qos   = int(qos) if qos in ["0", "1", "2"] else 0
    retain = parse("-r")
    retain = retain.lower() == "true" or retain == "1"

    mm = None
    
    # Conectar si se especifica -h
    if "-h" in args:
        mm = MqttManager(client_id=sdata.sid, server=host, port=port, user=user, password=passw)
        mm.set_callback(on_message_received)
        
        if mm.debug:
            print(f"Connecting MQTT {host}:{port}... ")
        
        mm.mqtt_connect(host, port, recon)
        
        if not mm.ping():
            print("No connected")
            return
    else:
        print("-h is required to connect")
        return

    # Comandos
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
            mm.msgs_loop(on_message_received)
        else:
            print("Subscribe failed")
        
    elif cmd == "listsub":
        print(mm.mqtt_list_subs())
        
    elif cmd == "unsub":
        if not "-t" in args or topic == "":
            print("-t required")
            return
        success = mm.mqtt_unsub(topic)
        #if success:
        print(f"Unsubscribe request sent for {topic}")
        #else:
        #    print("Unsubscribe may not be fully supported")

    elif cmd == "close":
        success = mm.mqtt_clean()
        if success:
            print("MQTT closed")
        else:
            print("MQTT close failed")
            
    elif cmd == "ping":
        success = mm.ping()
        if success:
            print("MQTT ping successful")
        else:
            print("MQTT ping failed")
        
    elif cmd == "listen":
        mm.msgs_loop(on_message_received)
        
    else:
        print(f"Invalid subcommand {cmd}")