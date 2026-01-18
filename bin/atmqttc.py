
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

    #TODO: add qos, reconnect and others parms

    if len(args) == 0 or "--h" in args:
        print("MQTT Command line utility for AT-ESP serial modem")
        print("Usage:\t First command executed connect with -h <host> [-p <port> -u <user> -P <pasword> -R <reconnect>]")
        print("\t atmqttc <pub> -t <topic> -m <message> [-q <qos> -r <retain>]")
        print("\t atmqttc <sub> -t <topic> [-q <qos>]")
        print("\t atmqttc <listsub>")
        print("\t atmqttc <unsub>")
        print("\t atmqttc <close>")
        print("\t atmqttc <listen> or [-l], [-v] verbose, [-tm] timings")
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
    
    qos   = parse("-q")
    qos   = int(qos) if qos in ["1", "2"] else 0
    retain = parse("-r")
    retain = 1 if retain == "1" else 0

    mm = MqttManager() # default dev= sdata.modem0
    
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
        utls.setenv("atmqttc", "")
        print("MQTT closed")

    elif cmd == "listen" or "-l" in args:
        print("Listening MQTT messages...")
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
    else:
       print(f"MQTT not valid subcommand {cmd}")            

    # Callback example
    #if "-ll" in args:
    #    print("Listening MQTT messages...")
    #    mm.msgs_loop(callback=on_message_received)
