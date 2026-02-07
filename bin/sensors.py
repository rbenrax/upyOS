import sys
import machine
import sdata

def get_esp32_sensors():
    sensors = {}
    try:
        import esp32
        # Temperature
        # Try mcu_temperature (newer chips like C3, C6)
        if hasattr(esp32, 'mcu_temperature'):
            try:
                tc = esp32.mcu_temperature()
                tf = (tc * 1.8) + 32.0
                sensors["Temp"] = f"{tc:.1f}C ({tf:.1f}F)"
            except:
                pass
        
        # Try raw_temperature (older chips like WROOM-32)
        if "Temp" not in sensors and hasattr(esp32, 'raw_temperature'):
            try:
                tf = esp32.raw_temperature()
                if tf > 0: 
                    tc = (tf - 32.0) / 1.8
                    sensors["Temp"] = f"{tf}F ({tc:.1f}C)"
            except:
                pass
        
        # Hall Sensor (Available on older ESP32, not on C3/C6/S2/S3 usually)
        if hasattr(esp32, 'hall_sensor'):
            try:
                sensors["Hall"] = str(esp32.hall_sensor())
            except:
                pass
            
    except ImportError:
        pass
    return sensors

def get_rp2_sensors():
    sensors = {}
    try:
        # RP2040 Internal Temperature sensor is on ADC(4)
        adc = machine.ADC(4)
        reading = adc.read_u16() * (3.3 / 65535)
        # 27 - (ADC_voltage - 0.706)/0.001721
        temperature = 27 - (reading - 0.706)/0.001721
        sensors["Temp"] = f"{temperature:.1f}C"
    except:
        pass
    return sensors

def __main__(args):
    if len(args) == 1 and args[0] == "--h":
        print("Show system sensors\nUsage: sensors")
        return

    platform = sys.platform
    print(f"System: {platform}")
    
    sensors = {}
    
    if platform == "esp32":
        sensors = get_esp32_sensors()
    elif platform == "rp2":
        sensors = get_rp2_sensors()
    # Add hooks for other platforms here
    
    if not sensors:
        print("No internal sensors detected or supported for this platform.")
    else:
        for name, value in sensors.items():
            print(f"{name}: {value}")

    # Log error if debug is enabled (simulating original logic)
    if not sensors and sdata.debug:
        print(f"Debug: Platform {platform} sensor reading failed or not implemented.")
