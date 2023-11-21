import os
import urequests
import machine
import utime
import usocket
import ussl

import utls

user='rbenrax'
repository='upyOS'
default_branch = 'main'
    
#------

#giturl = f'https://github.com/{user}/{repository}'
#url_tree = f'https://api.github.com/repos/{user}/{repository}/git/trees/{default_branch}?recursive=1'
url_raw = f'https://raw.githubusercontent.com/{user}/{repository}/master/'

#def pull_git_tree(u_tree):
#    headers = {'User-Agent': 'upyOS'} 
#    r = urequests.get(u_tree, headers=headers)
#    #print(r.content.decode('utf-8'))

def pull2(f_path, url):
    _, _, host, path = url.split('/', 3)
    
    #print(f"{f_path} {url} {host} {path}")
    
    # Crear un socket
    s = usocket.socket()
    
    ai = usocket.getaddrinfo(host, 443)
    addr = ai[0][-1]
    
    # Conectar al servidor
    s.connect(addr)
    
    # Crear un socket SSL
    ssl_socket = ussl.wrap_socket(s)
    
    # Agregar un encabezado 'User-Agent' a la solicitud HTTPS
    solicitud = 'GET /%s HTTP/1.0\r\nHost: %s\r\nUser-Agent: upyOS\r\n\r\n' % (path, host)
    
    # Enviar la solicitud al servidor
    ssl_socket.write(bytes(solicitud, 'utf8'))
    # Leer la respuesta del servidor

    headers_received = False

    with open(f_path, 'w') as f:            
        while True:
            chunk = ssl_socket.read(512)  # Puedes ajustar el tamaño del búfer según tus necesidades
            if not chunk:
                break
            
            #print(chunk.decode('utf8'))
            if not headers_received:
                # Buscar el final de las cabeceras
                end_of_headers = chunk.find(b'\r\n\r\n')
                if end_of_headers != -1:
                    headers_received = True
                    # Agregar solo el cuerpo de la respuesta después del final de las cabeceras
                    #data += chunk[end_of_headers + 4:]
                    f.write(chunk[end_of_headers + 4:].decode('utf-8'))
                else:
                    # Si no se han recibido las cabeceras completas, continuar leyendo
                    continue
            else:
                f.write(chunk.decode('utf-8'))

    
    # Cerrar el socket después de leer todos los datos
    ssl_socket.close()
    s.close()

    return

def pull(f_path, raw_url):

    try:
  
        headers = {'User-Agent': 'upyOS'} 
        r = urequests.get(raw_url, headers=headers)
  
        with open(f_path, 'w') as f:
            f.write(r.content.decode('utf-8'))
            #print(r.content.decode('utf-8'))
            
    except Exception as ex:
        print('pull error: ' + ex)
    
def __main__(args):

    if len(args) == 1 and args[0]=="--h":
        print("Upgrade upyOS from git repository\nUsage: upgrade <options>: -r reboot after upgrade")
        return
    else:
    
        print("upyOs OTA Upgrade, downloading upgradde list")
        uf="/etc/upgrade.inf"
        pull2(uf, url_raw + uf[1:])
        
        if not utls.file_exists(uf):
            print("No upgrade file available, system can not be upgraded")
            return
            
        r = input("Confirm upyOS upgrade (y/N)? ")
        if r!="y":
            print("Upgrade canceled"
            return
              
        print("Upgrading from upyOS git repsitory, wait...")
        with open(uf, 'r') as f:
            while True:
                fp=f.readline()
                if not fp: break
                fp=fp[:-1] # remove ending CR
                print(fp)
                pull2(fp, url_raw + fp[1:])
                
        #os.remove(uf)
        print("\nUpgrade complete")
        utime.sleep(2)
        
        if len(args) == 1 and args[0]=="-r":
            print("Rebooting...")
            utime.sleep(2)
            machine.soft_reset()

