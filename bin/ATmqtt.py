
# MQTT manager

from ATmodem import ModemManager
import time
import sdata
import utls

proc=None

class MqttManager(ModemManager):
    
    def __init__(self, sctrl=False, scmds=True, sresp=True):
        super().__init__(sctrl, scmds, sresp)

        self.debug = False # Debug?
        self.buffer = "" # Message buffer
        
    # MQTT CMDs

    def mqtt_user(self, schem=1, client="", user="", passw="", cert_key_ID=0, CA_ID=0, path=""):
        """Configurar  al broker MQTT (AT+MQTTCONN)"""
                   #AT+MQTTUSERCFG=0,1,"ESP32-C2","","",0,0,""
        command = f'AT+MQTTUSERCFG=0,{schem},"{client}","{user}","{passw}",{cert_key_ID},{CA_ID},"{path}"'
        sts, _ = self.atCMD(command, 1)
        return sts

    def mqtt_connect(self, host="", port=1883, reconnect=0):
        """Conectar al broker MQTT (AT+MQTTCONN)"""
                    #AT+MQTTCONN=0,"192.168.1.5",1883,0
        command = f'AT+MQTTCONN=0,"{host}",{port},{reconnect}'
        sts, _ = self.atCMD(command, "+MQTTCONNECTED:0", 3)
        return sts
    
    def mqtt_pub(self, topic="", data="", qos=0, retain=0):
        sts, _ = self.atCMD(f'AT+MQTTPUB=0,"{topic}","{data}",{qos},{retain}', 1)
        return sts
    
    def mqtt_sub(self, topic="", qos=0):
        sts, resp = self.atCMD(f'AT+MQTTSUB=0,"{topic}",{qos}', 1)
        return sts
    
    def mqtt_list_subs(self):
        sts, res = self.atCMD(f'AT+MQTTSUB?', 1)
        if sts:
            return res
        return ""

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
        if sdata.m0.any():
            data = sdata.m0.read()
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
    
    def monitor_loop(self, callback=None):
        """
        Bucle continuo de monitoreo de mensajes MQTT
        
        Args:
            callback: Función a llamar cuando se recibe un mensaje
                     Debe aceptar un dict con el mensaje parseado
        """
        print("Iniciando monitoreo de mensajes MQTT...")
        print("Presiona Ctrl+C para detener")
        
        try:
            while True:
 
                # Thread control
                if proc.sts=="S":break
        
                if proc.sts=="H":
                    utime.sleep(1)
                    continue
                
                messages = self.check_messages()
                
                for msg in messages:
                    if callback:
                        callback(msg)
                
                time.sleep_ms(10)  # Pequeña pausa para no saturar
                
        except KeyboardInterrupt:
            print("\nMonitoreo detenido")





# Callback ejemplo de uso
def on_message_received(msg):
    """Callback personalizado para procesar mensajes"""
    #print(f"\n>>> Callback ejecutado <<<")
    #print(f"Tópico: {msg['topic']}")
    #print(f"Mensaje: {msg['data']}")
    
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

    mm = MqttManager(sctrl=False, scmds=False, sresp=False)
    
    # If modem not connected
    if not sdata.m0:
        print("Connecting ...")
        mm.executeScript("/local/dial.inf") # Connection script
    
    # Else Wifi Connection by program
    #mm.resetHW(22, 2)
    #if not mm.createUART(1, 115200, 4, 5):
    #    return
    
    #mm.wifi_connect("DIGIFIBRA-cGPRi","")
    
    print("Test: "    + str(mm.test_modem()))
    print("Version: " + mm.get_version())
    print("IP: "      + mm.get_ip_mac("ip"))
    print("MAC: "     + mm.get_ip_mac("mac"))

    print(f"Conectando MQTT")
    mm.mqtt_user(1, "rp2040", "", "")
    if mm.mqtt_connect("192.168.1.5"):

        mm.mqtt_pub("casa/buhardilla", "hola=rp2040")

        mm.mqtt_sub("casa/sotano/temp")
        mm.mqtt_sub("casa/sotano/hum")
        print(mm.mqtt_list_subs())
        
    #    mm.mqtt_unsub("casa/sotano")
    #    print(mm.mqtt_list_subs())

        mm.monitor_loop(callback=on_message_received)
        
        # Manual 
        #print("Comprobando mensajes MQTT...")
        #while True:
        #    messages = mm.check_messages()
        #    if messages:
        #        for msg in messages:
        #            print(f"Nuevo mensaje en '{msg['topic']}': {msg['data']}")
        #    time.sleep(0.1)
       
