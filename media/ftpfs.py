
#!/usr/bin/env python3
"""
FTP FUSE Filesystem - Monta servidores FTP como directorios locales
Requisitos: pip install fusepy
Uso: python ftpfs.py <host> <punto_montaje> [opciones]
"""

import os
import sys
import stat
import errno
import ftplib
from datetime import datetime
from io import BytesIO
from fuse import FUSE, FuseOSError, Operations
import argparse
import logging

class FTPFS(Operations):
    def __init__(self, host, port=21, user='anonymous', passwd='', encoding='utf-8'):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.encoding = encoding
        self.ftp_cache = {}
        self.dir_cache = {}
        self.cache_timeout = 5
        
    def _get_ftp(self):
        """Obtiene o crea una conexión FTP"""
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.host, self.port)
            ftp.login(self.user, self.passwd)
            ftp.encoding = self.encoding
            return ftp
        except Exception as e:
            logging.error(f"Error conectando a FTP: {e}")
            raise FuseOSError(errno.ECONNREFUSED)
    
    def _parse_list_line(self, line):
        """Parsea una línea de LIST de FTP"""
        parts = line.split(None, 8)
        if len(parts) < 9:
            return None
        
        perms = parts[0]
        size = int(parts[4]) if parts[4].isdigit() else 0
        name = parts[8]
        
        is_dir = perms.startswith('d')
        is_link = perms.startswith('l')
        
        return {
            'name': name,
            'size': size,
            'is_dir': is_dir,
            'is_link': is_link,
            'perms': perms
        }
    
    def _list_dir(self, path):
        """Lista el contenido de un directorio con caché"""
        cache_key = path
        if cache_key in self.dir_cache:
            return self.dir_cache[cache_key]
        
        ftp = self._get_ftp()
        try:
            items = []
            lines = []
            ftp.dir(path, lines.append)
            
            for line in lines:
                item = self._parse_list_line(line)
                if item and item['name'] not in ['.', '..']:
                    items.append(item)
            
            self.dir_cache[cache_key] = items
            return items
        except ftplib.error_perm as e:
            logging.error(f"Error listando {path}: {e}")
            raise FuseOSError(errno.ENOENT)
        finally:
            ftp.quit()
    
    def _get_item(self, path):
        """Obtiene información de un archivo o directorio"""
        if path == '/':
            return {'name': '/', 'is_dir': True, 'size': 0}
        
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        
        items = self._list_dir(dirname if dirname else '/')
        for item in items:
            if item['name'] == basename:
                return item
        
        return None
    
    def getattr(self, path, fh=None):
        """Obtiene atributos de un archivo/directorio"""
        item = self._get_item(path)
        if item is None:
            raise FuseOSError(errno.ENOENT)
        
        mode = 0o755 if item['is_dir'] else 0o644
        nlink = 2 if item['is_dir'] else 1
        
        return {
            'st_mode': (stat.S_IFDIR | mode) if item['is_dir'] else (stat.S_IFREG | mode),
            'st_nlink': nlink,
            'st_size': item['size'],
            'st_ctime': 0,
            'st_mtime': 0,
            'st_atime': 0,
        }
    
    def readdir(self, path, fh):
        """Lee el contenido de un directorio"""
        items = self._list_dir(path if path != '/' else '')
        
        dirents = ['.', '..']
        dirents.extend([item['name'] for item in items])
        
        return dirents
    
    def read(self, path, size, offset, fh):
        """Lee datos de un archivo"""
        ftp = self._get_ftp()
        try:
            data = BytesIO()
            ftp.retrbinary(f'RETR {path}', data.write)
            content = data.getvalue()
            return content[offset:offset + size]
        except ftplib.error_perm as e:
            logging.error(f"Error leyendo {path}: {e}")
            raise FuseOSError(errno.EACCES)
        finally:
            ftp.quit()
    
    def write(self, path, data, offset, fh):
        """Escribe datos en un archivo"""
        ftp = self._get_ftp()
        try:
            # Leer contenido existente si hay offset
            if offset > 0:
                existing = BytesIO()
                try:
                    ftp.retrbinary(f'RETR {path}', existing.write)
                    existing_data = existing.getvalue()
                except:
                    existing_data = b''
            else:
                existing_data = b''
            
            # Combinar datos
            new_data = existing_data[:offset] + data
            
            # Subir archivo
            ftp.storbinary(f'STOR {path}', BytesIO(new_data))
            
            # Invalidar caché
            dirname = os.path.dirname(path)
            if dirname in self.dir_cache:
                del self.dir_cache[dirname]
            
            return len(data)
        except ftplib.error_perm as e:
            logging.error(f"Error escribiendo {path}: {e}")
            raise FuseOSError(errno.EACCES)
        finally:
            ftp.quit()
    
    def create(self, path, mode, fi=None):
        """Crea un nuevo archivo"""
        ftp = self._get_ftp()
        try:
            ftp.storbinary(f'STOR {path}', BytesIO(b''))
            
            # Invalidar caché
            dirname = os.path.dirname(path)
            if dirname in self.dir_cache:
                del self.dir_cache[dirname]
            
            return 0
        finally:
            ftp.quit()
    
    def unlink(self, path):
        """Elimina un archivo"""
        ftp = self._get_ftp()
        try:
            ftp.delete(path)
            
            # Invalidar caché
            dirname = os.path.dirname(path)
            if dirname in self.dir_cache:
                del self.dir_cache[dirname]
        except ftplib.error_perm as e:
            logging.error(f"Error eliminando {path}: {e}")
            raise FuseOSError(errno.EACCES)
        finally:
            ftp.quit()
    
    def mkdir(self, path, mode):
        """Crea un directorio"""
        ftp = self._get_ftp()
        try:
            ftp.mkd(path)
            
            # Invalidar caché
            dirname = os.path.dirname(path)
            if dirname in self.dir_cache:
                del self.dir_cache[dirname]
        except ftplib.error_perm as e:
            logging.error(f"Error creando directorio {path}: {e}")
            raise FuseOSError(errno.EACCES)
        finally:
            ftp.quit()
    
    def rmdir(self, path):
        """Elimina un directorio"""
        ftp = self._get_ftp()
        try:
            ftp.rmd(path)
            
            # Invalidar caché
            dirname = os.path.dirname(path)
            if dirname in self.dir_cache:
                del self.dir_cache[dirname]
        except ftplib.error_perm as e:
            logging.error(f"Error eliminando directorio {path}: {e}")
            raise FuseOSError(errno.EACCES)
        finally:
            ftp.quit()
    
    def rename(self, old, new):
        """Renombra un archivo o directorio"""
        ftp = self._get_ftp()
        try:
            ftp.rename(old, new)
            
            # Invalidar caché
            for p in [old, new]:
                dirname = os.path.dirname(p)
                if dirname in self.dir_cache:
                    del self.dir_cache[dirname]
        except ftplib.error_perm as e:
            logging.error(f"Error renombrando {old} a {new}: {e}")
            raise FuseOSError(errno.EACCES)
        finally:
            ftp.quit()
    
    def chmod(self, path, mode):
        """Cambia permisos (no soportado en FTP estándar)"""
        return 0
    
    def chown(self, path, uid, gid):
        """Cambia propietario (no soportado en FTP estándar)"""
        return 0

def main():
    parser = argparse.ArgumentParser(
        description='Monta un servidor FTP como sistema de archivos local'
    )
    parser.add_argument('host', help='Servidor FTP (ejemplo: ftp.ejemplo.com)')
    parser.add_argument('mountpoint', help='Punto de montaje local')
    parser.add_argument('-p', '--port', type=int, default=21, help='Puerto FTP (default: 21)')
    parser.add_argument('-u', '--user', default='anonymous', help='Usuario FTP')
    parser.add_argument('-P', '--password', default='', help='Contraseña FTP')
    parser.add_argument('-e', '--encoding', default='utf-8', help='Codificación (default: utf-8)')
    parser.add_argument('-d', '--debug', action='store_true', help='Modo debug')
    parser.add_argument('-f', '--foreground', action='store_true', help='Ejecutar en primer plano')
    
    args = parser.parse_args()
    
    # Configurar logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Verificar punto de montaje
    if not os.path.isdir(args.mountpoint):
        print(f"Error: {args.mountpoint} no existe o no es un directorio")
        sys.exit(1)
    
    print(f"Montando {args.host} en {args.mountpoint}")
    print(f"Usuario: {args.user}")
    print(f"Para desmontar: fusermount -u {args.mountpoint}")
    
    # Crear filesystem
    ftpfs = FTPFS(
        host=args.host,
        port=args.port,
        user=args.user,
        passwd=args.password,
        encoding=args.encoding
    )
    
    # Montar
    FUSE(
        ftpfs,
        args.mountpoint,
        nothreads=True,
        foreground=args.foreground,
        allow_other=False
    )

if __name__ == '__main__':
    main()
