import os
import utls

try:
    import usys as sys
except ImportError:
    import sys

try:
    import uio as io
except ImportError:
    import io

try:
    from uio import IOBase
except ImportError:
    class IOBase: pass

try:
    import builtins
except ImportError:
    # Some MicroPython versions use __builtins__ directly or other names
    import __main__ as builtins 

# Stream wrapper for MicroPython compatibility (emulates UART/Socket)
class StreamWrapper(IOBase):
    def __init__(self):
        self.buffer = io.StringIO()
    def write(self, data):
        if isinstance(data, (bytes, bytearray)):
            try: data = data.decode()
            except: data = str(data)
        if data: self.buffer.write(data)
        return len(data)
    def readinto(self, buf):
        return 0
    def ioctl(self, op, arg):
        if op == 4: # MP_STREAM_FLUSH
            return 0
        return 0
    def getvalue(self):
        return self.buffer.getvalue()

# JSON helper
def sendJSON(httpResponse, data):
    httpResponse.WriteResponseJSONOk(obj=data)

def sendError(httpResponse, code, msg):
    httpResponse.WriteResponseJSONError(code, obj={'error': msg})

import json

# --- Auth ---
ALLOWED_TOKEN = None
USER_CREDENTIALS = {}

def load_credentials():
    global USER_CREDENTIALS
    paths = ['etc/system.conf', '/etc/system.conf']
    for p in paths:
        try:
            with open(p, 'r') as f:
                conf = json.load(f)
                USER_CREDENTIALS = conf.get('auth', {})
                print(f"Loaded credentials from {p}")
                return
        except OSError:
            continue
    print("Error: system.conf not found in", paths)

load_credentials()

def check_auth(func):
    def wrapper(httpClient, httpResponse, *args, **kwargs):
        # Allow if no password set
        if not USER_CREDENTIALS.get('paswd'):
            return func(httpClient, httpResponse, *args, **kwargs)
            
        cookie = httpClient.GetRequestHeaders().get('Cookie', '')
        if 'auth_token=valid_session' in cookie:
             return func(httpClient, httpResponse, *args, **kwargs)
             
        httpResponse.WriteResponseError(401)
    return wrapper

def login_handler(httpClient, httpResponse):
    data = httpClient.ReadRequestContentAsJSON()
    user = data.get('user')
    password = data.get('password')
    
    expected_user = USER_CREDENTIALS.get('user')
    expected_pass = USER_CREDENTIALS.get('paswd')

    if user == expected_user and utls.sha1(password) == expected_pass:
        httpResponse.WriteResponseOk(
            headers={'Set-Cookie': 'auth_token=valid_session; Path=/'},
            contentType="application/json",
            content=json.dumps({'status': 'ok'})
        )
    else:
        httpResponse.WriteResponseJSONError(401, obj={'error': 'Invalid credentials'})

def logout_handler(httpClient, httpResponse):
    httpResponse.WriteResponseOk(
        headers={'Set-Cookie': 'auth_token=; Path=/; Max-Age=0'},
        contentType="application/json",
        content=json.dumps({'status': 'ok'})
    )

# --- Terminal WS (Callback) ---

try:
    try:
        from libx.microWebSocket import MicroWebSocket
    except ImportError:
        from microWebSocket import MicroWebSocket
except ImportError:
    MicroWebSocket = None

try:
    import _thread
except ImportError:
    pass

try:
    from uio import IOBase
except ImportError:
    class IOBase: pass

class WS_Terminal(IOBase):
    def __init__(self):
        self.ws = None
        self.lock = _thread.allocate_lock()
        self.rx_buf = []
        self._is_writing = False
    
    def accept_ws(self, ws, httpClient):
        self.ws = ws
        self.ws.RecvTextCallback = self.recv_text
        self.ws.ClosedCallback   = self.closed
        try:
            import uos
            try: uos.dupterm(None, 0)
            except: pass
            uos.dupterm(self, 0)
            if self.ws and not self.ws.IsClosed():
                self.ws.SendText(f"\r\nupyOS WebTerminal connected. {sys.platform}\r\n/ $: ")
        except Exception as e:
            print("WS_Terminal dupterm error:", e)

    def write(self, data):
        if self._is_writing or not self.ws or self.ws.IsClosed(): return len(data)
        self._is_writing = True
        try:
            if isinstance(data, (bytes, bytearray)):
                try: data = data.decode()
                except: data = str(data)
            if data: self.ws.SendText(data)
        except: pass
        finally: self._is_writing = False
        return len(data)

    def readinto(self, buf):
        self.lock.acquire()
        try:
            if not self.rx_buf: return None
            n = 0
            while self.rx_buf and n < len(buf):
                b = self.rx_buf.pop(0)
                buf[n] = ord(b) if isinstance(b, str) else b
                n += 1
            return n
        finally: self.lock.release()
            
    def ioctl(self, op, arg):
        if op == 3: return (1 if self.rx_buf else 0) | (4 if self.ws and not self.ws.IsClosed() else 0)
        if op == 4: self.close()
        return 0

    def close(self):
        if self.ws: self.ws.Close()

    def recv_text(self, ws, msg):
        self.lock.acquire()
        try:
            for char in msg: self.rx_buf.append(char)
        finally: self.lock.release()
        try:
            import uos
            if hasattr(uos, 'dupterm_notify'): uos.dupterm_notify(self)
        except: pass

    def closed(self, ws):
        try:
            import uos
            uos.dupterm(None, 0)
        except: pass

def ws_accept_callback(webSocket, httpClient) :
    if MicroWebSocket:
        WS_Terminal().accept_ws(webSocket, httpClient)
    else:
        webSocket.Close()

# --- File System Handlers ---

@check_auth
def fs_list_handler(httpClient, httpResponse):
    data = httpClient.ReadRequestContentAsJSON()
    path = data.get('path', '/') if data else '/'
    
    # Security check: prevent going above root if needed, but for now allow full access
    # consistent with existing shell access.
    
    try:
        entries = []
        if path == '': path = '/'
        
        # os.listdir in MicroPython/standard python
        # We need to distiguish files and dirs. 
        # In full Python os.scandir is better, but MicroPython os.listdir returns strings.
        # We'll use os.stat to check type.
        
        for name in os.listdir(path):
            full_path = path + '/' + name if path != '/' else '/' + name
            try:
                st = os.stat(full_path)
                is_dir = (st[0] & 0o170000) == 0o040000
                size = st[6]
                entries.append({
                    'name': name,
                    'is_dir': is_dir,
                    'size': size
                })
            except:
                pass # skip un-stat-able files
                
        sendJSON(httpResponse, {'entries': entries, 'path': path})
    except Exception as e:
        sendError(httpResponse, 500, str(e))

@check_auth
def fs_read_handler(httpClient, httpResponse):
    path = httpClient.GetRequestQueryParams().get('path')
    if not path:
        sendError(httpResponse, 400, "Missing path")
        return
        
    try:
        if not httpResponse.WriteResponseFile(path, contentType="text/plain"):
            sendError(httpResponse, 404, "File not found or empty")
    except Exception as e:
        sendError(httpResponse, 500, str(e))

@check_auth
def fs_write_handler(httpClient, httpResponse):
    path = httpClient.GetRequestQueryParams().get('path')
    if not path:
        sendError(httpResponse, 400, "Missing path")
        return
        
    contentLength = httpClient.GetRequestContentLength()
    
    try:
        with open(path, 'w') as f:
            remaining = contentLength
            while remaining > 0:
                chunk_size = min(remaining, 1024)
                chunk = httpClient.ReadRequestContent(size=chunk_size)
                if not chunk:
                    break
                if isinstance(chunk, bytes):
                    chunk = chunk.decode()
                f.write(chunk)
                remaining -= len(chunk)
        sendJSON(httpResponse, {'status': 'ok'})
    except Exception as e:
        sendError(httpResponse, 500, str(e))

@check_auth
def fs_delete_handler(httpClient, httpResponse):
    data = httpClient.ReadRequestContentAsJSON()
    path = data.get('path')
    if not path:
        sendError(httpResponse, 400, "Missing path")
        return

    try:
        st = os.stat(path)
        is_dir = (st[0] & 0o170000) == 0o040000
        if is_dir:
            os.rmdir(path)
        else:
            os.remove(path)
        sendJSON(httpResponse, {'status': 'ok'})
    except Exception as e:
        sendError(httpResponse, 500, str(e))
        
@check_auth
def fs_rename_handler(httpClient, httpResponse):
    data = httpClient.ReadRequestContentAsJSON()
    old_path = data.get('old_path')
    new_path = data.get('new_path')
    
    if not old_path or not new_path:
        sendError(httpResponse, 400, "Missing old_path or new_path")
        return
        
    try:
        os.rename(old_path, new_path)
        sendJSON(httpResponse, {'status': 'ok'})
    except Exception as e:
        sendError(httpResponse, 500, str(e))

@check_auth
def fs_mkdir_handler(httpClient, httpResponse):
    data = httpClient.ReadRequestContentAsJSON()
    path = data.get('path')
    if not path:
        sendError(httpResponse, 400, "Missing path")
        return
        
    try:
        os.mkdir(path)
        sendJSON(httpResponse, {'status': 'ok'})
    except Exception as e:
        sendError(httpResponse, 500, str(e))

@check_auth
def fs_download_handler(httpClient, httpResponse):
    path = httpClient.GetRequestQueryParams().get('path')
    if not path:
        sendError(httpResponse, 400, "Missing path")
        return
        
    try:
        filename = path.split('/')[-1]
        headers = {
            "Content-Disposition": 'attachment; filename="%s"' % filename
        }
        if not httpResponse.WriteResponseFile(path, contentType="application/octet-stream", headers=headers):
            sendError(httpResponse, 404, "File not found or empty")
    except Exception as e:
        sendError(httpResponse, 500, str(e))

@check_auth
def fs_upload_handler(httpClient, httpResponse):
    path = httpClient.GetRequestQueryParams().get('path')
    if not path:
        sendError(httpResponse, 400, "Missing path")
        return

    contentLength = httpClient.GetRequestContentLength()
    if contentLength <= 0:
        sendError(httpResponse, 400, "Missing or invalid Content-Length")
        return

    try:
        with open(path, 'wb') as f:
            remaining = contentLength
            while remaining > 0:
                chunk_size = min(remaining, 1024)
                chunk = httpClient.ReadRequestContent(size=chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                remaining -= len(chunk)
        
        if remaining == 0:
            sendJSON(httpResponse, {'status': 'ok'})
        else:
            sendError(httpResponse, 500, "Incomplete upload")
    except Exception as e:
        sendError(httpResponse, 500, str(e))

# --- GPIO Handlers ---
# Mocking machine if strictly running on PC for testing, 
# but writing for MicroPython. 
# We will use try/except import to handle test environment.

try:
    from machine import Pin
except ImportError:
    # Mock Pin class for non-MicroPython envs
    class Pin:
        IN = 0
        OUT = 1
        PULL_UP = 1
        PULL_DOWN = 2
        
        def __init__(self, id, mode=-1, pull=-1):
            self.id = id
            self.mode = mode
            self.value_ = 0
            
        def value(self, v=None):
            if v is not None:
                self.value_ = v
            return self.value_

@check_auth
def gpio_status_handler(httpClient, httpResponse):
    import sdata
    
    # Use GPIOs from board configuration if available
    pin_map = {} # GPIO -> Board Pin
    if isinstance(sdata.board.get('gpio'), list):
        for gpio_group in sdata.board['gpio']:
            if isinstance(gpio_group, dict):
                for gpio_id_str, board_pin in gpio_group.items():
                    try:
                        gpio_id = int(gpio_id_str)
                        pin_map[gpio_id] = board_pin
                    except ValueError:
                        pass
    
    # Fallback to common pins if no board config found
    if not pin_map:
        for p in [0, 1, 2, 3, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33]:
            pin_map[p] = p
    
    pins_to_check = sorted(pin_map.keys())
    
    pins_data = []
    for g_id in pins_to_check:
        try:
            val = Pin(g_id).value()
            pins_data.append({
                'gpio': g_id, 
                'pin': pin_map[g_id], 
                'val': val
            })
        except:
            pass

    # Extract board leds (ledio)
    leds_data = []
    if isinstance(sdata.board.get('ledio'), list):
        for led_group in sdata.board['ledio']:
            if isinstance(led_group, dict):
                for label, g_id in led_group.items():
                    try:
                        val = Pin(int(g_id)).value()
                        leds_data.append({'label': label, 'gpio': g_id, 'val': val})
                    except:
                        pass

    # Extract rgb info (rgbio)
    rgb_data = []
    if isinstance(sdata.board.get('rgbio'), list):
        for rgb_group in sdata.board['rgbio']:
            if isinstance(rgb_group, dict):
                for label, g_id in rgb_group.items():
                    rgb_data.append({'label': label, 'gpio': g_id})
            
    sendJSON(httpResponse, {
        'pins': pins_data,
        'leds': leds_data,
        'rgb': rgb_data
    })

@check_auth
def rgb_set_handler(httpClient, httpResponse):
    data = httpClient.ReadRequestContentAsJSON()
    gpio = data.get('gpio')
    r = data.get('r', 0)
    g = data.get('g', 0)
    b = data.get('b', 0)
    
    if gpio is None:
        sendError(httpResponse, 400, "Missing gpio")
        return
        
    try:
        import neopixel
        from machine import Pin
        np = neopixel.NeoPixel(Pin(int(gpio)), 1)
        np[0] = (int(r), int(g), int(b))
        np.write()
        sendJSON(httpResponse, {'status': 'ok'})
    except Exception as e:
        sendError(httpResponse, 500, str(e))

@check_auth
def gpio_set_handler(httpClient, httpResponse):
    data = httpClient.ReadRequestContentAsJSON()
    pin_id = data.get('pin')
    val = data.get('val')
    
    if pin_id is None or val is None:
        sendError(httpResponse, 400, "Missing pin or val")
        return
        
    try:
        p = Pin(pin_id, Pin.OUT)
        p.value(int(val))
        sendJSON(httpResponse, {'status': 'ok', 'pin': pin_id, 'val': val})
    except Exception as e:
        sendError(httpResponse, 500, str(e))

@check_auth
def cmd_run_handler(httpClient, httpResponse):
    data = httpClient.ReadRequestContentAsJSON()
    cmd = data.get('cmd')
    
    if not cmd:
        sendError(httpResponse, 400, "Missing cmd")
        return
        
    try:
        import sdata
        
        # Capture output using dupterm or direct assignment
        wrapper = StreamWrapper()
        capture_active = False
        
        try:
            # Try dupterm first as it's more standard in MicroPython for redirection
            import uos
            # We use index 0 which is usually the default console
            uos.dupterm(wrapper, 0)
            capture_active = "dupterm"
        except:
            try:
                # Fallback to sys.stdout assignment if dupterm fails
                old_stdout = sys.stdout
                sys.stdout = wrapper
                capture_active = "stdout"
            except:
                pass

        # Protect against input() blocking
        orig_input = None
        try:
            if hasattr(builtins, 'input'):
                orig_input = builtins.input
                def blocked_input(*args, **kwargs):
                    raise Exception("Interactive input() is not supported in upyDesktop. Use utelnetd.")
                builtins.input = blocked_input
        except:
            pass

        try:
            sdata.upyos.run_cmd(cmd)
            # Remove leading/trailing vertical whitespace, preserve internal alignment
            output = wrapper.getvalue().strip('\r\n')
        finally:
            if orig_input:
                builtins.input = orig_input
            
            if capture_active == "dupterm":
                import uos
                uos.dupterm(None, 0)
            elif capture_active == "stdout":
                sys.stdout = old_stdout

        if not output:
             output = "Command executed (no output)\n"

        import uos
        sendJSON(httpResponse, {'status': 'ok', 'cmd': cmd, 'output': output, 'cwd': uos.getcwd()})
    except Exception as e:
        sendError(httpResponse, 500, str(e))

@check_auth
def cmd_interrupt_handler(httpClient, httpResponse):
    # Send response first to avoid NetworkError in browser
    sendJSON(httpResponse, {'status': 'ok', 'msg': 'Interrupt signal sent'})
    
    try:
        import sdata
        import machine
        import utime
        
        # Give some time for the TCP response to be sent before disrupting the system
        utime.sleep_ms(300)
        
        # Safe list of services not to stop
        services = ["uhttpd", "utelnetd", "uftpd"]
        
        # Stop background processes by setting status to "S" (Stop)
        for p in sdata.procs:
            if p.cmd not in services:
                p.sts = "S"
        
        # General signal to stop current execution in the main thread
        if hasattr(machine, 'KeyboardInterrupt'):
            try:
                machine.KeyboardInterrupt()
            except:
                pass
    except:
        pass

@check_auth
def system_reset_handler(httpClient, httpResponse):
    try:
        import machine
        import utime
        # Try to send response before reset
        try:
            sendJSON(httpResponse, {'status': 'ok', 'msg': 'Resetting MCU...'})
            utime.sleep(0.5)
        except:
            pass
        machine.reset()
    except Exception as e:
        sendError(httpResponse, 500, str(e))

# --- System Status Handlers ---

@check_auth
def system_status_handler(httpClient, httpResponse):
    try:
        import sdata
        import gc
        import uos
        
        # Storage
        bit_tuple = uos.statvfs("/")
        blksize = bit_tuple[0]
        total_storage = bit_tuple[2] * blksize
        free_storage = bit_tuple[3] * blksize
        
        # Memory
        free_mem = gc.mem_free()
        alloc_mem = gc.mem_alloc()
        total_mem = free_mem + alloc_mem
        
        # Board Info
        # Accessing nested dicts safely in case sdata is not fully populated in test env
        mcu_type = "Unknown"
        mcu_arch = "Unknown"
        board_name = "Unknown"
        board_vendor = "Unknown"
        
        try:
             mcu_type = sdata.board["mcu"][0]["type"]
             mcu_arch = sdata.board["mcu"][0]["arch"]
             board_name = sdata.board["board"]["name"]
             board_vendor = sdata.board["board"]["vendor"]
        except:
             pass

        # Services status
        services = {
            "utelnetd": "utelnetserver" in sys.modules,
            "uftpd": "uftpdserver" in sys.modules,
            "uhttpd": "microWebSrv" in sys.modules 
        }
        # Fallback check in sdata.procs just in case
        for p in sdata.procs:
            if p.cmd == "utelnetd": services["utelnetd"] = True
            if p.cmd == "uftpd": services["uftpd"] = True
            if p.cmd == "uhttpd": services["uhttpd"] = True

        # Filter board config for display
        board_config = {}
        excluded_keys = ['mcu', 'board', 'gpio', 'ledio', 'rgbio']
        try:
            for k, v in sdata.board.items():
                if k not in excluded_keys:
                    board_config[k] = v
        except:
            pass

        # CPU Temp
        cpu_temp = 0
        try:
            import esp32
            # raw_temperature returns Fahrenheit on some ports, but let's check basic availability
            # Note: On recent ESP32 ports, raw_temperature() might be deprecated or removed.
            # Convert F to C: (F - 32) / 1.8
            try:
                cpu_temp = esp32.mcu_temperature()
            except:
                f = esp32.raw_temperature()
                cpu_temp = (f - 32) / 1.8
        except:
            try:
                # RP2040 standard temp sensor
                import machine
                sensor_temp = machine.ADC(4)
                conversion_factor = 3.3 / (65535)
                reading = sensor_temp.read_u16() * conversion_factor
                cpu_temp = 27 - (reading - 0.706)/0.001721
            except:
                pass

        import uos
        info = {
            'mcu': {'type': mcu_type, 'arch': mcu_arch},
            'board': {'name': board_name, 'vendor': board_vendor},
            'config': board_config,
            'memory': {'total': total_mem, 'free': free_mem, 'alloc': alloc_mem},
            'storage': {'total': total_storage, 'free': free_storage},
            'sys': {
                'name': sdata.name, 
                'version': sdata.version, 
                'id': sdata.sid,
                'cpu_freq': 0,
                'cpu_temp': cpu_temp,
                'cwd': uos.getcwd()
            },
            'services': services
        }
        
        try:
            import machine
            info['sys']['cpu_freq'] = machine.freq()
        except:
            pass

        sendJSON(httpResponse, info)
    except Exception as e:
        sendError(httpResponse, 500, str(e))


# --- Routes definition ---

routes = [
    # Auth
    ( "/api/login", "POST", login_handler ),
    ( "/api/logout", "GET", logout_handler ),
    
    # Status
    ( "/api/status", "GET", system_status_handler ),
    ( "/api/system/reset", "POST", system_reset_handler ),
    
    # Command
    ( "/api/cmd/run", "POST", cmd_run_handler ),
    ( "/api/cmd/interrupt", "POST", cmd_interrupt_handler ),

    # File System
    ( "/api/fs/list",   "POST", fs_list_handler ),
    ( "/api/fs/read",    "GET",  fs_read_handler ),
    ( "/api/fs/write",   "POST", fs_write_handler ),
    ( "/api/fs/delete", "POST", fs_delete_handler ),
    ( "/api/fs/rename", "POST", fs_rename_handler ),
    ( "/api/fs/mkdir",  "POST", fs_mkdir_handler ),
    ( "/api/fs/download", "GET", fs_download_handler ),
    ( "/api/fs/upload", "POST", fs_upload_handler ),
    
    # GPIO
    ( "/api/gpio/status", "GET", gpio_status_handler ),
    ( "/api/gpio/set",    "POST", gpio_set_handler ),
    ( "/api/rgb/set",     "POST", rgb_set_handler ),
]
