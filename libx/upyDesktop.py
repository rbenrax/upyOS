
import os
import sys

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

    if user == expected_user and password == expected_pass:
        httpResponse.WriteResponseOk(
            headers={'Set-Cookie': 'auth_token=valid_session; Path=/'},
            contentType="application/json",
            content=json.dumps({'status': 'ok'})
        )
    else:
        httpResponse.WriteResponseJSONError(401, obj={'error': 'Invalid credentials'})

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
    data = httpClient.ReadRequestContentAsJSON()
    path = data.get('path')
    if not path:
        sendError(httpResponse, 400, "Missing path")
        return
        
    try:
        with open(path, 'r') as f:
            content = f.read()
        sendJSON(httpResponse, {'content': content})
    except Exception as e:
        sendError(httpResponse, 500, str(e))

@check_auth
def fs_write_handler(httpClient, httpResponse):
    data = httpClient.ReadRequestContentAsJSON()
    path = data.get('path')
    content = data.get('content')
    
    if not path or content is None:
        sendError(httpResponse, 400, "Missing path or content")
        return
        
    try:
        with open(path, 'w') as f:
            f.write(content)
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
    # This is tricky because we don't know exactly which pins are available 
    # and safe to query on every board.
    # We will just return a comprehensive list of "common" ESP32 pins for now.
    # In a real scenario, this might need configuration.
    
    common_pins = [0, 1, 2, 3, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33]
    
    pins_data = []
    for p_id in common_pins:
        try:
            # We just create a pin object to read it? 
            # DANGEROUS: Creating Pin object might reset its mode.
            # Ideally we would track state. For this demo, we will just 
            # pretend we can read the value if it's already set up, 
            # or just default to 0. 
            # SAFEST: Only report what we can without disturbing.
            # But users want to see status.
            
            # For the dashboard demo, we'll just mock the reading or read if it's safe.
            # In MicroPython, `Pin(n).value()` reads input.
            val = Pin(p_id).value()
            pins_data.append({'pin': p_id, 'val': val})
        except:
            pass
            
    sendJSON(httpResponse, {'pins': pins_data})

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
        sdata.upyos.run_cmd(cmd)
        # run_cmd does not return output, but prints to stdout. 
        # We confirm execution value.
        sendJSON(httpResponse, {'status': 'ok', 'cmd': cmd, 'output': 'Command executed\n (output sent to serial/stdout, Use utelnetd if you want remote access to a full terminal)'})
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

        info = {
            'mcu': {'type': mcu_type, 'arch': mcu_arch},
            'board': {'name': board_name, 'vendor': board_vendor},
            'memory': {'total': total_mem, 'free': free_mem, 'alloc': alloc_mem},
            'storage': {'total': total_storage, 'free': free_storage},
            'sys': {'name': sdata.name, 'version': sdata.version}
        }
        sendJSON(httpResponse, info)
    except Exception as e:
        sendError(httpResponse, 500, str(e))


# --- Routes definition ---

routes = [
    # Auth
    ( "/api/login", "POST", login_handler ),
    
    # Status
    ( "/api/status", "GET", system_status_handler ),
    
    # Command
    ( "/api/cmd/run", "POST", cmd_run_handler ),

    # File System
    ( "/api/fs/list",   "POST", fs_list_handler ),
    ( "/api/fs/read",   "POST", fs_read_handler ),
    ( "/api/fs/write",  "POST", fs_write_handler ),
    ( "/api/fs/delete", "POST", fs_delete_handler ),
    ( "/api/fs/rename", "POST", fs_rename_handler ),
    ( "/api/fs/mkdir",  "POST", fs_mkdir_handler ),
    
    # GPIO
    ( "/api/gpio/status", "GET", gpio_status_handler ),
    ( "/api/gpio/set",    "POST", gpio_set_handler ),
]
