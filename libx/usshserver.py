import socket
import network
import uos
import errno
import gc
import ssl
from uio import IOBase

import sdata
import utls

# Debugging and test flags
DEBUG_TLS = True
TEST_ECHO = True

last_client_socket = None
server_socket = None

try:
    import uselect
    _uselect_available = True
except:
    _uselect_available = False

class SSLSocketWrapper(IOBase):
    """
    Wrapper para socket SSL compatible con dupterm.
    Basado en el mismo principio que WS_Terminal en upyDesktop.
    """
    
    def __init__(self, ssl_socket):
        self.socket = ssl_socket
        self.discard_count = 0
        self._rx_buf = bytearray()  # Buffer de recepción
        
    def _poll_socket(self):
        """Verifica si hay datos disponibles y los lee al buffer"""
        try:
            # Leer datos disponibles sin bloquear
            data = self.socket.recv(64)
            if data:
                self._rx_buf.extend(data)
                return len(data)
        except OSError as e:
            if e.args[0] != errno.EAGAIN:
                raise
        return 0
        
    def readinto(self, b):
        """Lee datos del buffer interno (llamado por dupterm/REPL)"""
        # Intentar llenar el buffer si está vacío
        if not self._rx_buf:
            self._poll_socket()
        
        # Si sigue vacío, no hay datos
        if not self._rx_buf:
            return None
            
        # Procesar bytes del buffer
        readbytes = 0
        for i in range(len(b)):
            if not self._rx_buf:
                break
                
            byte = self._rx_buf.pop(0)
            
            # Filtrar IAC Telnet
            if byte == 0xFF:
                # Descartar secuencia IAC (3 bytes)
                if len(self._rx_buf) >= 2:
                    self._rx_buf.pop(0)
                    self._rx_buf.pop(0)
                continue
                
            # Convertir LF a CR
            if byte == 10:
                byte = 13
                
            b[i] = byte
            readbytes += 1
            
        return readbytes if readbytes > 0 else None
    
    def write(self, data):
        """Escribe datos al socket SSL"""
        try:
            return self.socket.send(data)
        except OSError as e:
            if e.args[0] in (104, 32, 110, 9, 128):
                return 0
            raise
    
    def ioctl(self, op, arg):
        """ioctl para polling por parte del sistema"""
        if op == 3:  # MP_STREAM_POLL
            # POLLIN - verificar si hay datos para leer
            if arg & 1:
                if self._rx_buf:
                    return 1
                # Intentar poll sin bloquear
                self._poll_socket()
                return 1 if self._rx_buf else 0
            # POLLOUT - siempre listo para escribir
            if arg & 4:
                return 1
        return 0
    
    def close(self):
        try:
            self.socket.close()
        except:
            pass


def read_input(sock, mask=None):
    """Lee entrada del usuario durante autenticación"""
    val = bytearray()
    while True:
        try:
            char = sock.recv(1)
            if not char:
                break
            
            byte = char[0]
            
            # IAC Telnet
            if byte == 0xFF:
                cmd = sock.recv(1)
                if cmd and ord(cmd) >= 251 and ord(cmd) <= 254:
                    sock.recv(1)
                continue
            
            if byte == 13 or byte == 10:  # CR o LF
                sock.sendall(b'\r\n')
                break
                
            if byte == 0x08 or byte == 0x7F:  # Backspace
                if val:
                    val.pop()
                    sock.sendall(b'\x08 \x08')
                continue
            
            if byte >= 32:  # Caracter imprimible
                val.append(byte)
                if mask:
                    sock.sendall(mask.encode())
                else:
                    sock.sendall(char)
                    
        except:
            break
    
    return val.decode()


def accept_telnet_connect(telnet_server):
    """Acepta conexión y configura dupterm"""
    global last_client_socket
    
    # Cerrar conexión anterior
    if last_client_socket:
        uos.dupterm(None)
        try:
            last_client_socket.close()
        except:
            pass
        last_client_socket = None
    
    gc.collect()
    
    try:
        raw_socket, remote_addr = telnet_server.accept()
        
        # Cargar certificados
        cert_file = "etc/cert.pem"
        key_file = "etc/key.pem"
        
        if not utls.file_exists(cert_file):
            cert_file = "cert.pem"
            key_file = "key.pem"
        
        if not utls.file_exists(cert_file):
            raw_socket.sendall(b'ERROR: SSL certificates not found\r\n')
            raw_socket.close()
            return
        
        # Crear socket SSL
        with open(key_file, 'rb') as f:
            key_data = f.read()
        with open(cert_file, 'rb') as f:
            cert_data = f.read()
        
        ssl_socket = ssl.wrap_socket(raw_socket, server_side=True, key=key_data, cert=cert_data)
        last_client_socket = ssl_socket
        
        utls.log("SecureTelnet", f"Connection from: {remote_addr}")
        
        # Negociar Telnet
        ssl_socket.sendall(bytes([255, 252, 34, 255, 251, 1]))
        ssl_socket.sendall(b'Secure System: ' + sdata.sid + b'\r\n')
        
        # Autenticación
        if sdata.sysconfig["auth"]["paswd"]:
            ssl_socket.sendall(b'Login: ')
            user = read_input(ssl_socket)
            
            ssl_socket.sendall(b'Password: ')
            pasw = read_input(ssl_socket, mask="*")
            
            if (sdata.sysconfig["auth"]["user"] != user or 
                sdata.sysconfig["auth"]["paswd"] != utls.sha1(pasw)):
                ssl_socket.sendall(b'Not logged in.\r\n')
                ssl_socket.close()
                last_client_socket = None
                return
            
            ssl_socket.sendall(b'Logged in ok\r\n')
            # Modo de depuración: echo loop simple (para debugging TLS/dupterm)
            if TEST_ECHO:
                ssl_socket.write(b'Entering echo-test mode. Type "exit" to leave.\r\n')
                while True:
                    ssl_socket.write(b'/ $: ')
                    line = read_input(ssl_socket)
                    if line is None:
                        break
                    if line.strip() == "exit":
                        break
                    if line.startswith("echo "):
                        ssl_socket.write(line[5:].encode() + b"\r\n")
                    else:
                        ssl_socket.write(b"Unknown command\r\n")
                ssl_socket.close()
                last_client_socket = None
                return
        else:
            ssl_socket.sendall(b'No password set\r\n')
        
        # Configurar dupterm
        ssl_socket.setblocking(False)
        wrapper = SSLSocketWrapper(ssl_socket)
        uos.dupterm(wrapper)
        
        utls.log("SecureTelnet", f"Session active: {remote_addr}")
        
    except Exception as e:
        print(f"SSHD Error: {e}")


def stop():
    """Detiene el servidor"""
    global server_socket, last_client_socket
    
    uos.dupterm(None)
    
    if last_client_socket:
        try:
            last_client_socket.close()
        except:
            pass
        last_client_socket = None
    
    if server_socket:
        try:
            server_socket.close()
        except:
            pass
        server_socket = None
    
    gc.collect()


def start(port=22):
    """Inicia servidor SSHD"""
    global server_socket
    
    stop()
    
    try:
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
                ip = wlan.ifconfig()[0]
                print(f"SSHD started on {ip}:{port}")
                print(f"Connect: openssl s_client -connect {ip}:{port} -quiet")
                
    except Exception as e:
        print(f"SSHD start error: {e}")
