# busca - BLE device finder with WS2812 proximity LED
# Optimized for Xiaomi Buds 4 detection

import bluetooth
import machine
import time
import neopixel

# --- Configuration ---
LED_GPIO = 8
LED_COUNT = 1
LED_BPP = 4           # RGBW (use 3 for RGB-only WS2812)

TX_POWER = -59         # estimated RSSI at 1 meter (calibrate for your buds)
N_PATH_LOSS = 2.5      # path loss exponent (2.0=open air, 3.0=indoors)

RSSI_BUFFER_SIZE = 8   # readings to keep per device
RSSI_OUTLIER_DB = 15   # discard readings that differ more than this from median
DEVICE_TIMEOUT_MS = 8000  # purge devices not seen for this long
DISPLAY_INTERVAL_S = 2    # seconds between screen updates

DEFAULT_KEYWORDS = ["buds", "xiaomi", "redmi"]
DEFAULT_MFR_IDS = [0x038F]  # Xiaomi manufacturer ID (little-endian: 8F 03)

# --- Global state ---
devices = {}       # mac -> {name, rssi_buf, last_seen, manufacturer_match}
target_mac = None  # optional: known MAC prefix/full to track
target_keywords = DEFAULT_KEYWORDS[:]
target_mfr_ids = DEFAULT_MFR_IDS[:]
ble = None
np = None


def decode_adv_fields(payload):
    """Parse all AD structures from BLE advertisement payload."""
    name = None
    mfr_ids = []
    svc_uuids = []

    i = 0
    while i < len(payload):
        if i >= len(payload):
            break
        length = payload[i]
        if length == 0:
            break
        if i + length >= len(payload):
            break

        ad_type = payload[i + 1]
        ad_data = payload[i + 2:i + 1 + length]

        # Complete / Shortened Local Name
        if ad_type in (0x08, 0x09):
            try:
                name = ad_data.decode('utf-8')
            except Exception:
                pass

        # Manufacturer Specific Data (first 2 bytes = company ID, little-endian)
        elif ad_type == 0xFF and len(ad_data) >= 2:
            company_id = ad_data[0] | (ad_data[1] << 8)
            mfr_ids.append(company_id)

        # 16-bit Service UUIDs (complete/incomplete)
        elif ad_type in (0x02, 0x03) and len(ad_data) >= 2:
            for j in range(0, len(ad_data) - 1, 2):
                uuid16 = ad_data[j] | (ad_data[j + 1] << 8)
                svc_uuids.append(uuid16)

        i += 1 + length

    return name, mfr_ids, svc_uuids


def is_target(name, mfr_ids):
    """Check if device matches filter criteria."""
    # Match by manufacturer IDs
    for tid in target_mfr_ids:
        if tid in mfr_ids:
            return True

    # Match by name keywords
    if name:
        lname = name.lower()
        for k in target_keywords:
            if k in lname:
                return True

    return False


def median(values):
    """Compute median of a list."""
    s = sorted(values)
    n = len(s)
    if n == 0:
        return 0
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) // 2


def filtered_rssi(rssi_buf):
    """Compute filtered RSSI: discard outliers then take median."""
    if not rssi_buf:
        return -100

    med = median(rssi_buf)

    # Discard outliers
    filtered = [r for r in rssi_buf if abs(r - med) <= RSSI_OUTLIER_DB]

    if not filtered:
        return med

    return median(filtered)


def rssi_trend(rssi_buf):
    """Detect RSSI trend: +1=improving(closer), -1=worsening(farther), 0=stable."""
    if len(rssi_buf) < 3:
        return 0

    # Compare average of recent half vs older half
    mid = len(rssi_buf) // 2
    old_avg = sum(rssi_buf[:mid]) / mid
    new_avg = sum(rssi_buf[mid:]) / (len(rssi_buf) - mid)
    diff = new_avg - old_avg

    if diff > 2:
        return 1   # getting closer (RSSI increasing)
    elif diff < -2:
        return -1  # getting farther (RSSI decreasing)
    return 0


def estimate_distance(rssi):
    """Estimate distance in meters from RSSI using log-distance path loss model."""
    if rssi >= TX_POWER:
        return 0.1
    distance = 10 ** ((TX_POWER - rssi) / (10 * N_PATH_LOSS))
    return round(distance, 2)


def rssi_bar(rssi):
    """Visual RSSI bar for terminal output."""
    level = max(0, min(10, int((rssi + 100) / 5)))
    return "[" + "#" * level + "-" * (10 - level) + "]"


def update_led(dist, trend):
    """Update WS2812 LED color based on distance and trend."""
    if np is None:
        return

    if dist < 0.5:
        # Very close - bright green, solid
        r, g, b = 0, 255, 0
    elif dist < 1.0:
        # Close - green
        r, g, b = 0, 180, 0
    elif dist < 3.0:
        # Medium - yellow
        r, g, b = 200, 200, 0
    elif dist < 5.0:
        # Far - orange
        r, g, b = 255, 100, 0
    else:
        # Very far - red
        r, g, b = 255, 0, 0

    # Trend overlay: blue pulse if approaching
    if trend > 0:
        b = min(255, b + 80)

    w = 0
    if LED_BPP == 4:
        np[0] = (r, g, b, w)
    else:
        np[0] = (r, g, b)
    np.write()


def led_off():
    """Turn off WS2812 LED."""
    if np is None:
        return
    if LED_BPP == 4:
        np[0] = (0, 0, 0, 0)
    else:
        np[0] = (0, 0, 0)
    np.write()


def blink_led(dist):
    """Calculate blink state based on distance and current time."""
    if dist < 0.5:
        return True  # solid on

    # Blink frequency increases with distance
    if dist < 1.0:
        period_ms = 800
    elif dist < 3.0:
        period_ms = 400
    elif dist < 5.0:
        period_ms = 200
    else:
        period_ms = 100

    # Use time to determine on/off phase (50% duty)
    return (time.ticks_ms() % period_ms) < (period_ms // 2)


def bt_irq(event, data):
    """BLE scan result callback."""
    if event != 5:  # _IRQ_SCAN_RESULT
        return

    addr_type, addr, adv_type, rssi, adv_data = data
    mac = ':'.join('%02X' % b for b in addr)

    # If tracking a specific MAC/prefix, check match
    if target_mac and not mac.startswith(target_mac):
        return

    name, mfr_ids, svc_uuids = decode_adv_fields(adv_data)

    # Check for manufacturer match in IDs
    mfr_match = False
    for tid in target_mfr_ids:
        if tid in mfr_ids:
            mfr_match = True
            break

    if target_mac:
        # Tracking specific MAC - always accept
        pass
    elif not is_target(name, mfr_ids):
        return

    now = time.ticks_ms()

    if mac in devices:
        dev = devices[mac]
        # Update name if we got a better one
        if name and not dev['name']:
            dev['name'] = name
        if mfr_match:
            dev['mfr'] = True
        # Add RSSI to buffer
        dev['buf'].append(rssi)
        if len(dev['buf']) > RSSI_BUFFER_SIZE:
            dev['buf'].pop(0)
        dev['seen'] = now
    else:
        devices[mac] = {
            'name': name,
            'buf': [rssi],
            'seen': now,
            'mfr': mfr_match,
        }


def find_best_target():
    """Find the best (strongest) target device from tracked devices."""
    now = time.ticks_ms()
    best_mac = None
    best_rssi = -200

    for mac, dev in devices.items():
        if time.ticks_diff(now, dev['seen']) > DEVICE_TIMEOUT_MS:
            continue
        rssi = filtered_rssi(dev['buf'])
        if rssi > best_rssi:
            best_rssi = rssi
            best_mac = mac

    return best_mac


def purge_old_devices():
    """Remove devices not seen recently."""
    now = time.ticks_ms()
    to_remove = []
    for mac, dev in devices.items():
        if time.ticks_diff(now, dev['seen']) > DEVICE_TIMEOUT_MS:
            to_remove.append(mac)
    for mac in to_remove:
        del devices[mac]


def scan_loop():
    """Main scanning loop with LED feedback."""
    # Start continuous scan: duration=0 (indefinite), interval=100ms, window=100ms
    ble.gap_scan(0, 100000, 100000)

    last_display = 0

    try:
        while True:
            now = time.ticks_ms()

            # Purge stale devices
            purge_old_devices()

            # Find best target and update LED
            best_mac = find_best_target()

            if best_mac:
                dev = devices[best_mac]
                rssi = filtered_rssi(dev['buf'])
                dist = estimate_distance(rssi)
                trend = rssi_trend(dev['buf'])

                # LED feedback with blink
                if blink_led(dist):
                    update_led(dist, trend)
                else:
                    led_off()
            else:
                led_off()

            # Display status periodically
            if time.ticks_diff(now, last_display) >= DISPLAY_INTERVAL_S * 1000:
                last_display = now
                print("\n--- BLE devices detected ---")

                if not devices:
                    print("  (none)")
                else:
                    for mac, dev in devices.items():
                        if time.ticks_diff(now, dev['seen']) > DEVICE_TIMEOUT_MS:
                            continue

                        rssi = filtered_rssi(dev['buf'])
                        dist = estimate_distance(rssi)
                        trend = rssi_trend(dev['buf'])

                        marker = " <-- TARGET" if mac == best_mac else ""
                        trend_sym = " ^" if trend > 0 else (" v" if trend < 0 else " =")

                        print(mac + marker)
                        print("  Name:", dev['name'] or "(no name)")
                        if dev['mfr']:
                            print("  Manufacturer match found (ID)")
                        print("  RSSI:", rssi, rssi_bar(rssi), trend_sym)
                        print("  Samples:", len(dev['buf']))
                        print("  Distance:", dist, "m")

                        if dist < 0.5:
                            print("  >> VERY CLOSE")
                        elif dist < 1:
                            print("  >> CLOSE")
                        elif dist < 3:
                            print("  >> MEDIUM")
                        elif dist < 5:
                            print("  >> FAR")
                        else:
                            print("  >> VERY FAR")
                        print()

            time.sleep_ms(50)  # small delay to avoid busy loop

    except KeyboardInterrupt:
        pass
    finally:
        ble.gap_scan(None)
        led_off()
        print("\nScan stopped.")


def __main__(args):
    global ble, np, target_mac

    if "--h" in args:
        print("busca - BLE headphone finder")
        print("Usage: busca [MAC_PART] [-mfr ID1,ID2] [-key K1,K2] [-tx N] [-n FACTOR]")
        print()
        print("  MAC_PART     MAC address or prefix (e.g., AA:BB or AA:BB:CC:DD:EE:FF)")
        print("  -mfr ID      Manufacturer IDs in hex (default: 0x038F)")
        print("  -key WORD    Name keywords (default: buds,xiaomi,redmi)")
        print("  -tx N        RSSI power at 1m (default: -59)")
        print("  -n FACTOR    Environmental loss factor (default: 2.5)")
        print("  -gpio PIN    WS2812 LED GPIO (default: 8)")
        print("  --noled      Disable WS2812 LED")
        print()
        print("Example: busca AA:BB:CC")
        print("         busca -mfr 0x004C -key airpods")
        return

    global TX_POWER, N_PATH_LOSS, LED_GPIO, target_keywords, target_mfr_ids

    use_led = True

    # Parse arguments
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "-tx" and i + 1 < len(args):
            TX_POWER = int(args[i + 1])
            i += 2
        elif arg == "-n" and i + 1 < len(args):
            N_PATH_LOSS = float(args[i + 1])
            i += 2
        elif arg == "-mfr" and i + 1 < len(args):
            mfr_input = args[i + 1].split(',')
            target_mfr_ids = [int(x, 16) for x in mfr_input]
            i += 2
        elif arg == "-key" and i + 1 < len(args):
            target_keywords = [x.lower() for x in args[i + 1].split(',')]
            i += 2
        elif arg == "-gpio" and i + 1 < len(args):
            LED_GPIO = int(args[i + 1])
            i += 2
        elif arg == "--noled":
            use_led = False
            i += 1
        elif ":" in arg:
            # MAC address or prefix
            target_mac = arg.upper()
            i += 1
        else:
            i += 1

    # Initialize BLE
    ble = bluetooth.BLE()
    ble.active(True)
    ble.irq(bt_irq)

    # Initialize WS2812 LED
    if use_led:
        try:
            np = neopixel.NeoPixel(machine.Pin(LED_GPIO), LED_COUNT, bpp=LED_BPP)
            led_off()
            print("WS2812 LED on GPIO", LED_GPIO, "active")
        except Exception as e:
            print("Warning: Could not initialize WS2812 LED:", e)
            np = None

    if target_mac:
        print("Searching for MAC patterns:", target_mac)
    else:
        print("Searching for target devices...")
        print("Keywords:", ", ".join(target_keywords))
        print("Mfr IDs:", ", ".join([hex(x) for x in target_mfr_ids]))

    print("TX_POWER:", TX_POWER, "dBm | Path loss:", N_PATH_LOSS)
    print("Ctrl+C to stop\n")

    scan_loop()


if __name__ == "__main__":
    __main__([])