
# MQTT utility client for ESP-AT modem

from esp_at import MqttManager
import time
import sdata
import utls
import sys

proc=None

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

    if len(args) == 0 or "--h" in args:
        print("MQTT Client - AT-ESP serial modem")
        print("Usage:\t First connect with -h <host> [-p <port> -u <user> -P <password> -R <reconnect>]")
        print("\t atmqttc <pub> -t <topic> -m <message> [-q <qos> -r <retain>]")
        print("\t atmqttc <lastwill> -t <topic> -m <message> [-q <qos> -r <retain>]")
        print("\t atmqttc <sub> -t <topic> [-q <qos>]")
        print("\t atmqttc <listsub>")
        print("\t atmqttc <unsub> -t <topic>")
        print("\t atmqttc <ping>")
        print("\t atmqttc <listen> [-l]")
        print("\t atmqttc <close>")
        print("\t Options: [-v] verbose, [-tm] timings, [-M <modemname>] (def: modem0)")
        return

    def parse(mod):
        try:
            if mod in args:
                i = args.index(mod)
                if i+1 < len(args):
                    return args[i + 1]
                else:
                    return ""
            else:
                return ""
        except Exception as ex:
            print("atmqttc modifier error, " + mod)
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
    
    device = parse("-M")
    if device == "":
        device = "modem0"

    qos   = parse("-q")
    qos   = int(qos) if qos in ["1", "2"] else 0
    retain = parse("-r")
    retain = 1 if retain == "1" else 0

    mm = MqttManager(device) # default dev= sdata.modem0
    
    # If modem not connected
    status = mm.wifi_status()
    if not mm.modem or status == "2" or status == "":
        print("No connected")
        return
    
    if "-v" in args:
        mm.sctrl = True
        mm.scmds = True
        mm.sresp = True
        args = [arg for arg in args if arg != "-v"]
        
    if "-tm" in args:
        mm.timing = True
        args = [arg for arg in args if arg != "-tm"]
    
    # WIFI Connection or alternative by atmodem -f modem.inf in /etc/init.sh
    #mm.resetHW(22, 2)
    #if not mm.createUART(1, 115200, 4, 5, "modem0"):
    #    return
    
    #mm.set_mode(1)
    #mm.wifi_connect("SSID","PASSW")
    
    #print("Test: "     + str(mm.test_modem()))
    #print("Version: "  + mm.get_version())
    #print("Local IP: " + mm.get_ip_mac("ip"))
    #print("MAC: "      + mm.get_ip_mac("mac"))

    #print(mm.set_ntp_server())
    #print(mm.set_datetime())

    connected = utls.getenv("atmqttc")
    
    if connected != "c":
        
        if not "-h" in args:
            print("-h required")
            return

        mm.mqtt_user(1, sdata.sid, user, passw)
        if mm.mqtt_connect(host, port, recon):
            utls.setenv("atmqttc", "c")
        else:
            utls.setenv("atmqttc", "")
            print("No connected")
            return

    if cmd == "pub":
        if not "-t" in args or topic == "":
            print("-t required")
            return
        if not "-m" in args or messg == "":
            print("-m required")
            return
        if mm.mqtt_pub(topic, messg, qos, retain):
            print(f"Message published")
        else:
            print(f"Publish failed")

    elif cmd == "lastwill":
        if not "-t" in args or topic == "":
            print("-t required")
            return
        if not "-m" in args or messg == "":
            print("-m required")
            return
        if mm.mqtt_conncfg(topic=topic, msg=messg, qos=qos, retain=retain):
            print("Last will configured")
        else:
            print("Last will configuration failed")

    elif cmd == "sub":
        if not "-t" in args or topic == "":
            print("-t required")
            return
        if mm.mqtt_sub(topic, qos):
            print(f"Subscribed to {topic}")
        else:
            print(f"Subscribe failed")

    elif cmd == "listsub":
        print(mm.mqtt_list_subs())
        
    elif cmd == "unsub":
        if not "-t" in args or topic == "":
            print("-t required")
            return
        if mm.mqtt_unsub(topic):
            print(f"Unsubscribed from {topic}")
        else:
            print(f"Unsubscribe failed")

    elif cmd == "close":
        mm.mqtt_clean()
        utls.setenv("atmqttc", "")
        print("MQTT closed")

    elif cmd == "ping":
        # Check MQTT connection status via MQTTCONN?
        sts, ret = mm.atCMD("AT+MQTTCONN?")
        if sts and "+MQTTCONNECTED" in ret or "3" in ret:
            print("MQTT ping ok")
        else:
            print("MQTT ping failed")

    elif cmd == "listen" or "-l" in args:
        print("Listening MQTT messages...")
        print("Ctrl+C to stop")
        try:
            while True:
                # Thread control
                if proc and proc.sts=="S":break

                if proc and proc.sts=="H":
                    time.sleep(1)
                    continue
                
                messages = mm.check_messages()
                if messages:
                    for msg in messages:
                        print(f"{msg['topic']}: {msg['data']}")
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nStopped listening")

    else:
        print(f"Invalid subcommand {cmd}")            

    # Callback example
    #if "-ll" in args:
    #    print("Listening MQTT messages...")
    #    mm.msgs_loop(callback=on_message_received)
