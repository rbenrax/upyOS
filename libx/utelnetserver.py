import socket
import network
import uos
import errno
import gc
from uio import IOBase

import sdata
import utls

last_client_socket = None
server_socket = None

# Provide necessary functions for dupterm and replace telnet control characters that come in.
class TelnetWrapper(IOBase):
    def __init__(self, socket):
        self.socket = socket
        self.discard_count = 0
        
    def readinto(self, b):
        readbytes = 0
        for i in range(len(b)):
            try:
                byte = 0
                # discard telnet control characters and
                # null bytes 
                while(byte == 0):
                    byte = self.socket.recv(1)[0]
                    if byte == 0xFF:
                        self.discard_count = 2
                        byte = 0
                    elif self.discard_count > 0:
                        self.discard_count -= 1
                        byte = 0
                    
                b[i] = byte
                
                readbytes += 1
            except (IndexError, OSError) as e:
                if type(e) == IndexError or len(e.args) > 0 and e.args[0] == errno.EAGAIN:
                    if readbytes == 0:
                        return None
                    else:
                        return readbytes
                # Handle common disconnection errors
                # ECONNRESET: 104, EPIPE: 32, ETIMEDOUT: 110, EBADF: 9, ENOTCONN: 128
                elif len(e.args) > 0 and e.args[0] in (104, 32, 110, 9, 128):
                    return 0 # Return 0 to indicate end of stream/disconnection
                else:
                    raise
        return readbytes
    
    def write(self, data):
        # we need to write all the data but it's a non-blocking socket
        # so loop until it's all written eating EAGAIN exceptions
        while len(data) > 0:
        
            try:
                written_bytes = self.socket.write(data)
                data = data[written_bytes:]
            except OSError as e:
                # EBADF (9) means socket is closed. EAGAIN means wait.
                # ECONNRESET (104), EPIPE (32), ETIMEDOUT (110) mean disconnection.
                if len(e.args) > 0:
                    if e.args[0] == errno.EAGAIN:
                        pass
                    elif e.args[0] in (9, 104, 32, 110, 128):
                        return # Stop writing, connection is gone
                    else:
                        raise
                else:
                    raise
    
    def close(self):
        self.socket.close()

# Helper function to read input (user/password) with Telnet IAC filtering
# Optimized to use bytearray to minimize memory allocation
def read_input(sock, mask=None):
    val = bytearray()
    while True:
        try:
            char = sock.recv(1)
            if not char:
                break # Connection closed
            
            # Telnet IAC (Interpret As Command) Handling
            if char == b'\xff':
                # Should be blocking read, so we expect the cmd byte
                cmd = sock.recv(1)
                if not cmd: break # Should not happen mid-sequence
                
                ord_cmd = ord(cmd)
                
                # WILL, WONT, DO, DONT take one parameter
                if ord_cmd >= 251 and ord_cmd <= 254:
                    sock.recv(1) # Consume option byte
                    continue
                
                # IAC IAC -> Literal 255
                if ord_cmd == 255:
                    # Proceed to process char (which is \xff)
                    # Let it fall through to printable check
                    pass 
                else:
                    # Other commands (SE, SB, etc) - simpler to ignore just the cmd byte for now
                    continue

            if char == b'\r':
                # Handle CR (Enter)
                # Try to consume an immediately following \n or \0
                sock.setblocking(False)
                try:
                    # Verify if there is a next byte immediately available
                    next_char = sock.recv(1)
                    if next_char != b'\n' and next_char != b'\0':
                        pass 
                except:
                    pass
                sock.setblocking(True)
                
                sock.sendall(b'\r\n')
                break
            
            if char == b'\n':
                sock.sendall(b'\r\n')
                break
                
            # Handle backspace (0x08) and DEL (0x7f)
            if char == b'\x08' or char == b'\x7f':
                if len(val) > 0:
                    val.pop()
                    sock.sendall(b'\x08 \x08')
                continue

            # Printable characters
            if char >= b' ':
                val.extend(char)
                if mask:
                    sock.sendall(mask.encode())
                else:
                    sock.sendall(char)
        except Exception:
            break
    return val.decode()

# Attach new clients to dupterm and 
# send telnet control characters to disable line mode
# and stop local echoing
def accept_telnet_connect(telnet_server):
    global last_client_socket
    
    if last_client_socket:
        # close any previous clients
        uos.dupterm(None)
        last_client_socket.close()
    
    # Run GC to free up memory before allocating new connection resources
    gc.collect()
    
    last_client_socket, remote_addr = telnet_server.accept()
    utls.log(f"Telnet", f"Connection from: {remote_addr}")
    
    # Negotiate Telnet options IMMEDIATELY to control echo and line mode
    # IAC WONT LINEMODE (255, 252, 34) - Force character mode
    # IAC WILL ECHO (255, 251, 1) - Server will handle echoing (essential for masking)
    last_client_socket.sendall(bytes([255, 252, 34])) 
    last_client_socket.sendall(bytes([255, 251, 1]))

    last_client_socket.sendall(b'System: ' + sdata.sid + b'\r\n')
    
    if sdata.sysconfig["auth"]["paswd"]!="":
    
        last_client_socket.setblocking(True)
        last_client_socket.settimeout(None) 
        
        last_client_socket.sendall(b'Login: ')
        user = read_input(last_client_socket, mask=None) # Echo ON for user
        
        last_client_socket.sendall(b'Password: ')
        pasw = read_input(last_client_socket, mask="*") # Echo '*' for password
        
        if sdata.sysconfig["auth"]["user"] != user or sdata.sysconfig["auth"]["paswd"] != utls.sha1(pasw):
            last_client_socket.sendall(b'Not logged in.\r\n')
            uos.dupterm(None)
            last_client_socket.close()
            utls.log(f"Telnet", f"Rejected connection from: {remote_addr} {user}")
            return
        else:
            utls.log(f"Telnet", f"Accepted connection from: {remote_addr} {user}")
            last_client_socket.sendall(b'Logged in ok, Press enter\r\n')

    else:
        last_client_socket.sendall(b'No password has been set, Press enter\r\n')
    
    last_client_socket.setblocking(False)
    last_client_socket.setsockopt(socket.SOL_SOCKET, 20, uos.dupterm_notify)
        
    uos.dupterm(TelnetWrapper(last_client_socket))

def stop():
    global server_socket, last_client_socket
    uos.dupterm(None)
    if server_socket:
        server_socket.close()
    if last_client_socket:
        last_client_socket.close()

# start listening for telnet connections on port 23
def start(port=23):
    stop()
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    ai = socket.getaddrinfo("0.0.0.0", port)
    addr = ai[0][4]
    
    server_socket.bind(addr)
    server_socket.listen(1)
    server_socket.setsockopt(socket.SOL_SOCKET, 20, accept_telnet_connect)
    
    for i in (network.AP_IF, network.STA_IF):
        wlan = network.WLAN(i)
        if wlan.active():
            print("Telnet server started on {}:{}".format(wlan.ifconfig()[0], port))
