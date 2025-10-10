#!/usr/bin/env python3
"""
FTP FUSE Filesystem - Monta servidores FTP como directorios locales
Versión mejorada con soporte para guardado confiable
Requisitos: pip install fusepy
Uso: python ftpfs.py <host> <punto_montaje> [opciones]
"""

import os
import sys
import stat
import errno
import ftplib
import argparse
import logging
import threading
import tempfile
from datetime import datetime
from io import BytesIO
from fuse import FUSE, FuseOSError, Operations

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
        
        # Sistema mejorado de cache de escritura
        self.write_cache = {}
        self.temp_files = {}
        self.file_handles = {}
        self.cache_lock = threading.Lock()
        self.handle_counter = 0
        
        # Crear directorio temporal para archivos en escritura
        self.temp_dir = tempfile.mkdtemp(prefix="ftpfs_")
        logging.info(f"Directorio temporal creado: {self.temp_dir}")

    def _get_ftp(self):
        """Obtiene o crea una conexión FTP con mejor manejo de errores"""
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.host, self.port, timeout=30)
            ftp.login(self.user, self.passwd)
            ftp.encoding = self.encoding
            ftp.set_pasv(True)  # Modo pasivo para mejor compatibilidad
            return ftp
        except Exception as e:
            logging.error(f"Error conectando a FTP {self.host}:{self.port}: {e}")
            raise FuseOSError(errno.ECONNREFUSED)

    def _parse_list_line(self, line):
        """Parsea una línea de LIST de FTP - compatible con diferentes servidores"""
        # Intentar formato UNIX/Linux
        parts = line.split()
        if len(parts) >= 9:
            perms = parts[0]
            # Buscar el nombre que puede contener espacios
            name = ' '.join(parts[8:])
            
            # Determinar si es directorio o enlace
            is_dir = perms.startswith('d')
            is_link = perms.startswith('l')
            
            try:
                size = int(parts[4]) if not is_dir else 0
            except ValueError:
                size = 0
                
            return {
                'name': name.rstrip(),
                'size': size,
                'is_dir': is_dir,
                'is_link': is_link,
                'perms': perms
            }
        
        # Intentar formato Windows
        if len(parts) >= 4:
            try:
                # Formato: fecha hora <DIR> nombre
                time_part = ' '.join(parts[0:2])
                dir_flag = parts[2]
                name = ' '.join(parts[3:])
                
                is_dir = (dir_flag == '<DIR>')
                size = 0 if is_dir else int(dir_flag)
                
                return {
                    'name': name.rstrip(),
                    'size': size,
                    'is_dir': is_dir,
                    'is_link': False,
                    'perms': 'drwxr-xr-x' if is_dir else '-rw-r--r--'
                }
            except (ValueError, IndexError):
                pass
        
        return None

    def _list_dir(self, path):
        """Lista el contenido de un directorio con caché"""
        cache_key = path
        if cache_key in self.dir_cache:
            return self.dir_cache[cache_key]
        
        ftp = self._get_ftp()
        try:
            items = []
            lines = []
            
            # Normalizar path para el comando LIST
            list_path = path if path != '/' else ''
            ftp.dir(list_path, lines.append)
            
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
            try:
                ftp.quit()
            except:
                pass

    def _get_item(self, path):
        """Obtiene información de un archivo o directorio"""
        if path == '/':
            return {'name': '/', 'is_dir': True, 'size': 0}
        
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        
        try:
            items = self._list_dir(dirname if dirname else '/')
            for item in items:
                if item['name'] == basename:
                    return item
        except FuseOSError:
            pass
        
        return None

    def getattr(self, path, fh=None):
        """Obtiene atributos de un archivo/directorio"""
        item = self._get_item(path)
        if item is None:
            raise FuseOSError(errno.ENOENT)
        
        # Permisos: lectura/escritura para usuario, solo lectura para otros
        mode = 0o755 if item['is_dir'] else 0o644
        nlink = 2 if item['is_dir'] else 1
        
        return {
            'st_mode': (stat.S_IFDIR | mode) if item['is_dir'] else (stat.S_IFREG | mode),
            'st_nlink': nlink,
            'st_size': item['size'],
            'st_ctime': 0,
            'st_mtime': 0,
            'st_atime': 0,
            'st_uid': os.getuid(),
            'st_gid': os.getgid(),
        }

    def readdir(self, path, fh):
        """Lee el contenido de un directorio"""
        items = self._list_dir(path if path != '/' else '')
        
        dirents = ['.', '..']
        dirents.extend([item['name'] for item in items])
        
        return dirents

    def open(self, path, flags):
        """Abrir archivo - necesario para VS Code"""
        with self.cache_lock:
            self.handle_counter += 1
            fh = self.handle_counter
            
            # Si el archivo se abre para escritura, preparar cache
            if flags & (os.O_WRONLY | os.O_RDWR):
                temp_path = os.path.join(self.temp_dir, f"temp_{fh}_{os.path.basename(path)}")
                self.temp_files[fh] = temp_path
                
                # Si existe el archivo remoto, descargarlo
                ftp = self._get_ftp()
                try:
                    with open(temp_path, 'wb') as f:
                        ftp.retrbinary(f'RETR {path}', f.write)
                except ftplib.error_perm:
                    # Archivo no existe, se creará nuevo
                    open(temp_path, 'wb').close()
                finally:
                    ftp.quit()
            
            self.file_handles[fh] = {'path': path, 'flags': flags}
            return fh

    def read(self, path, size, offset, fh):
        """Lee datos de un archivo"""
        # Si está en cache de escritura, leer del archivo temporal
        if fh in self.temp_files:
            try:
                with open(self.temp_files[fh], 'rb') as f:
                    f.seek(offset)
                    return f.read(size)
            except Exception as e:
                logging.error(f"Error leyendo cache temporal {path}: {e}")
                raise FuseOSError(errno.EIO)
        
        # Leer directamente del FTP
        ftp = self._get_ftp()
        try:
            data = BytesIO()
            ftp.retrbinary(f'RETR {path}', data.write)
            content = data.getvalue()
            
            if offset >= len(content):
                return b''
                
            return content[offset:offset + size]
        except ftplib.error_perm as e:
            logging.error(f"Error leyendo {path}: {e}")
            raise FuseOSError(errno.EACCES)
        finally:
            ftp.quit()

    def write(self, path, data, offset, fh):
        """Escribe datos en un archivo usando cache temporal"""
        if fh not in self.temp_files:
            # Si no hay handle de archivo, crear uno temporal
            with self.cache_lock:
                temp_path = os.path.join(self.temp_dir, f"temp_direct_{os.path.basename(path)}")
                self.temp_files[fh] = temp_path
                
                # Descargar archivo existente si existe
                ftp = self._get_ftp()
                try:
                    with open(temp_path, 'wb') as f:
                        ftp.retrbinary(f'RETR {path}', f.write)
                except ftplib.error_perm:
                    # Archivo no existe, crear nuevo
                    open(temp_path, 'wb').close()
                finally:
                    ftp.quit()
        
        # Escribir en archivo temporal
        try:
            with open(self.temp_files[fh], 'r+b') as f:
                f.seek(offset)
                f.write(data)
                f.flush()
            
            return len(data)
        except Exception as e:
            logging.error(f"Error escribiendo en cache temporal {path}: {e}")
            raise FuseOSError(errno.EIO)

    def flush(self, path, fh):
        """Sincronizar datos - importante para VS Code"""
        # Para FTP, flush no hace nada inmediatamente
        # La sincronización real ocurre en release/fsync
        return 0

    def fsync(self, path, fdatasync, fh):
        """Forzar sincronización - crítico para VS Code"""
        return self._upload_temp_file(fh)

    def release(self, path, fh):
        """Llamado cuando se cierra el archivo - SUBIR a FTP"""
        try:
            if fh in self.temp_files:
                self._upload_temp_file(fh)
        finally:
            # Limpiar recursos
            with self.cache_lock:
                if fh in self.temp_files:
                    temp_path = self.temp_files[fh]
                    if os.path.exists(temp_path):
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                    del self.temp_files[fh]
                if fh in self.file_handles:
                    del self.file_handles[fh]
        return 0

    def _upload_temp_file(self, fh):
        """Sube archivo temporal al servidor FTP"""
        if fh not in self.temp_files:
            return 0
            
        temp_path = self.temp_files[fh]
        if not os.path.exists(temp_path):
            return 0
            
        handle_info = self.file_handles.get(fh, {})
        path = handle_info.get('path', '')
        
        if not path:
            return 0
        
        ftp = self._get_ftp()
        try:
            with open(temp_path, 'rb') as f:
                ftp.storbinary(f'STOR {path}', f)
            
            # Invalidar caché del directorio
            dirname = os.path.dirname(path)
            if dirname in self.dir_cache:
                del self.dir_cache[dirname]
            
            logging.info(f"Archivo subido exitosamente: {path}")
            return 0
        except Exception as e:
            logging.error(f"Error subiendo {path}: {e}")
            raise FuseOSError(errno.EACCES)
        finally:
            ftp.quit()

    def create(self, path, mode, fi=None):
        """Crea un nuevo archivo"""
        ftp = self._get_ftp()
        try:
            # Crear archivo vacío
            ftp.storbinary(f'STOR {path}', BytesIO(b''))
            
            # Invalidar caché
            dirname = os.path.dirname(path)
            if dirname in self.dir_cache:
                del self.dir_cache[dirname]
            
            return self.open(path, os.O_WRONLY)
        except ftplib.error_perm as e:
            logging.error(f"Error creando {path}: {e}")
            raise FuseOSError(errno.EACCES)
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

    def truncate(self, path, length, fh=None):
        """Trunca un archivo - importante para operaciones de escritura"""
        if fh is not None and fh in self.temp_files:
            # Truncar archivo temporal
            with open(self.temp_files[fh], 'r+b') as f:
                f.truncate(length)
        else:
            # Para truncate sin file handle, usar método tradicional
            ftp = self._get_ftp()
            try:
                # Descargar, truncar y volver a subir
                data = BytesIO()
                ftp.retrbinary(f'RETR {path}', data.write)
                content = data.getvalue()[:length]
                ftp.storbinary(f'STOR {path}', BytesIO(content))
            except ftplib.error_perm as e:
                logging.error(f"Error truncando {path}: {e}")
                raise FuseOSError(errno.EACCES)
            finally:
                ftp.quit()
        return 0

    def chmod(self, path, mode):
        """Cambia permisos (no soportado en FTP estándar)"""
        return 0

    def chown(self, path, uid, gid):
        """Cambia propietario (no soportado en FTP estándar)"""
        return 0

    def utimens(self, path, times=None):
        """Actualiza timestamps (no soportado en FTP estándar)"""
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
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Verificar punto de montaje
    if not os.path.isdir(args.mountpoint):
        print(f"Error: {args.mountpoint} no existe o no es un directorio")
        sys.exit(1)
    
    print(f"Monting {args.host} en {args.mountpoint}")
    print(f"User: {args.user}")
    print(f"To unmount: fusermount -u {args.mountpoint}")
    print("VS Code suppot version")
    
    # Crear filesystem
    ftpfs = FTPFS(
        host=args.host,
        port=args.port,
        user=args.user,
        passwd=args.password,
        encoding=args.encoding
    )
    
    # Montar con opciones optimizadas para escritura
    try:
        FUSE(
            ftpfs,
            args.mountpoint,
            nothreads=False,  # Permitir hilos para mejor rendimiento
            foreground=args.foreground,
            allow_other=False,
            direct_io=True,   # Evitar cache intermedio de FUSE
            default_permissions=False,
            big_writes=True,  # Permitir escrituras grandes
            max_write=131072, # Tamaño máximo de escritura
            auto_cache=True   # Cache automático
        )
    except KeyboardInterrupt:
        print("\nDesmontando...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
