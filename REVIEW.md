# Revisión del Proyecto upyOS - Informe de Errores y Mejoras

**Fecha:** 2026-02-07  
**Versión revisada:** 0.9.4

---

## 🔴 ERRORES (Bugs)

### 1. `kernel.py:58` — Alias vacíos en sysconfig por defecto
```python
"alias" : {"": "", "": ""},
```
Se definen dos claves vacías `""` en el diccionario de alias. En Python, las claves duplicadas se sobrescriben, resultando en un solo par `{"": ""}`. Esto no tiene utilidad y debería ser un diccionario vacío o con ejemplos reales.

**Corrección sugerida:**
```python
"alias" : {},
```

---

### 2. `kernel.py:132-136` — Posible IndexError al acceder a `e[0]`
```python
for e in tmp:
    if e[0]=="$":
```
Si `tmp` contiene un string vacío `""`, acceder a `e[0]` lanzará un `IndexError`.

**Corrección sugerida:**
```python
for e in tmp:
    if e and e[0]=="$":
```

---

### 3. `proc.py:53` — Se pasa string vacío en lugar de lista vacía
```python
mod.__main__("") # TODO: no nice
```
La mayoría de los comandos esperan `args` como lista. Pasar `""` (string) puede causar que `len(args)` devuelva 0 pero `args[0]` devuelva `""` en lugar de fallar limpiamente. Algunos comandos como `free.py:7` hacen `args[0] if args else ""` que funcionaría con string, pero es inconsistente.

**Corrección sugerida:**
```python
mod.__main__([])
```

---

### 4. `ls.py:114` — `info()` puede devolver `0` en lugar de tupla
Cuando `info()` retorna `0` (para archivos ocultos, línea 23), la línea 114 intenta desempaquetar:
```python
size, is_dir = info(fullpath, mode)
```
Esto lanzará `TypeError: cannot unpack non-iterable int`.

**Corrección sugerida en `ls.py:info()`:**
```python
if filename[0] == ".": 
    return (0, False)
```
Y en la línea 29 (File not found):
```python
return (0, False)
```

---

### 5. `wifi.py:1-8` — Import de `network` fuera de función con fallback incompleto
```python
try:
    import network
except ImportError as ie:
    print("Networking is not implemented on this platform")
```
Si `network` no se importa, el resto del módulo a nivel global (líneas 40-67) que usa `network.STAT_IDLE`, etc., fallará con `NameError`. El import de `sleep` y `tspaces` en líneas 10-11 se ejecuta siempre, pero las constantes `NETSTAT` en línea 60 usan `network.*`.

**Corrección sugerida:** Mover las constantes `NETSTAT` dentro de `__main__()` o protegerlas con un `try/except`.

---

### 6. `wget.py:15-22` — Archivo nunca se cierra en caso de error + lectura puede fallar
```python
fp = open(filename, "wt")
r = urequests.get(url).raw
while (True):
    read = r.read(100)
    fp.write(read)
    if len(read) < 100:
        break
fp.close()
```
- No usa `with` statement, si hay excepción el archivo queda abierto.
- `r.read(100)` puede devolver `None` o `bytes`, y `fp.write()` espera `str` (modo `"wt"`).
- La respuesta `urequests.get(url)` nunca se cierra.

**Corrección sugerida:**
```python
r = urequests.get(url)
try:
    with open(filename, "wb") as fp:
        while True:
            chunk = r.raw.read(512)
            if not chunk:
                break
            fp.write(chunk)
finally:
    r.close()
```

---

### 7. `setauth.py:43` — Typo "fot" → "for"
```python
print(f"New password has been set fot user {args[0]}")
```

**Corrección:** `"for"` en lugar de `"fot"`.

---

### 8. `setauth.py:49` — Comillas anidadas problemáticas
```python
print(f"Curren user is {sdata.sysconfig["auth"]["user"]}")
```
En MicroPython esto puede funcionar en algunas versiones, pero es técnicamente incorrecto usar las mismas comillas dentro de un f-string. Además, "Curren" debería ser "Current".

**Corrección sugerida:**
```python
print(f"Current user is {sdata.sysconfig['auth']['user']}")
```

---

### 9. `test.py:12,15,18,26` — Siempre usa `args[1]` sin verificar el flag
```python
if "-f" in args:
    ret = utls.file_exists(args[1])
```
Si el usuario escribe `test -f` sin ruta, `args[1]` lanzará `IndexError`. Además, si el flag no está en posición 0, `args[1]` podría no ser la ruta.

**Corrección sugerida:** Buscar el índice del flag y usar el siguiente argumento:
```python
if "-f" in args:
    idx = args.index("-f")
    if idx + 1 < len(args):
        ret = utls.file_exists(args[idx + 1])
    else:
        print("test: missing argument after -f")
        return
```

---

### 10. `gpio.py:13-20` — Orden incorrecto de detección `>>` vs `>`
```python
if ">" in args:
    idx = args.index(">")
    ...
elif ">>" in args:
```
El `elif ">>"` nunca se ejecutará porque `">" in args` también es `True` cuando hay `">>"` en la lista. El orden debe ser invertido.

**Corrección sugerida:**
```python
if ">>" in args:
    idx = args.index(">>")
    ...
elif ">" in args:
    idx = args.index(">")
    ...
```

---

### 11. `upgrade.py:259` — Indentación incorrecta
```python
        if ftu == cont:
            print("]OK\n100% Upgrade complete.")
            print(f"{cntup} Upgraded files")
        else:
           print(f"]\nUpgrade not complete. {cont}/{ftu}")
```
La línea del `else` tiene 11 espacios de indentación en lugar de 12. Esto podría causar un `IndentationError` en Python estricto (aunque MicroPython puede ser más tolerante).

---

### 12. `cd.py:6` — Typo "Chage" → "Change"
```python
print("Chage current directory\nUsage: cd <path>")
```

---

### 13. `index.html` y `login.html` — Archivos casi duplicados
`index.html` y `login.html` son prácticamente idénticos (misma página de login). `login.html` tiene atributos extra (`autocapitalize`, `autocorrect`, `spellcheck`) que faltan en `index.html`. Esto genera confusión y mantenimiento duplicado.

**Sugerencia:** Eliminar uno y redirigir al otro, o unificarlos.

---

## 🟡 MEJORAS (Sugerencias)

### 14. `kernel.py:109` — `pass` redundante después de `except`
```python
except Exception as ex:
    print("cmd error, " + str(ex))
    if sdata.debug:
        sys.print_exception(ex)
    pass
```
El `pass` es innecesario aquí.

---

### 15. `kernel.py:23` — `os.uname()` está deprecado
```python
sdata.name = "upyOS-" + os.uname()[0]
```
En versiones recientes de MicroPython, `os.uname()` está deprecado en favor de `sys.platform`.

**Sugerencia:**
```python
sdata.name = "upyOS-" + sys.platform
```

---

### 16. `utls.py:128` — `except:` bare (sin tipo de excepción)
```python
try:
    if path in sdata.sysconfig.get("pfiles", []):
        return True
except:
    pass
```
Los `except:` sin tipo capturan todo, incluyendo `KeyboardInterrupt` y `SystemExit`. Es mejor usar `except Exception:`.

---

### 17. `proc.py:94` — Excepción siempre impresa (no respeta `sdata.debug`)
```python
except Exception as e:
    self.rmmod=True
    print(f"Error executing {self.cmd}")
    #if sdata.debug:
    sys.print_exception(e)
```
El `if sdata.debug:` está comentado, por lo que siempre se imprime el traceback completo. Debería restaurarse la condición.

---

### 18. `sdata.py:11` — Inconsistencia en nombre de variable
```python
upyos = None # Kernel instance
```
Pero en `kernel.py:26`:
```python
sdata.upyos = self
```
El nombre es consistente, pero el comentario en `sdata.py:8` dice `debug = True` como valor por defecto. Esto significa que en modo normal (sin `init.sh`), el debug está activado, lo cual puede ser confuso para usuarios finales.

---

### 19. `wifi.py:202`, `wifi.py:249`, `wifi.py:283` — `pass` redundante después de `except`
Múltiples bloques `except` terminan con `pass` innecesario cuando ya hay código en el bloque.

---

### 20. `echo.py:25` — `"".join()` no añade espacios entre argumentos
```python
f.write("".join(args[:idx]) + "\n")
```
Si el usuario escribe `echo hello world > file.txt`, se escribirá `"helloworld"` en lugar de `"hello world"`.

**Corrección sugerida:**
```python
f.write(" ".join(args[:idx]) + "\n")
```
Lo mismo aplica a las líneas 30, 32 y 39.

---

### 21. `grep.py:43` — Búsqueda desde directorio vacío
```python
search(txt, "", mode)
```
Se pasa `""` como path, lo que depende de que `uos.listdir("")` funcione como `uos.listdir(".")`. Sería más explícito usar `"."` o `uos.getcwd()`.

---

### 22. `cp.py:39-42` — Condición redundante
```python
if not utls.isdir(spath):
    cp(spath, dpath)
else:
    if utls.isdir(spath):  # Siempre True aquí
```
La segunda comprobación `if utls.isdir(spath)` es siempre `True` porque estamos en el `else` de `if not utls.isdir(spath)`.

---

### 23. `mv.py:32-35` — Misma condición redundante que `cp.py`
Mismo patrón duplicado.

---

### 24. `sleep.py:7` — Mensaje de ayuda incorrecto
```python
print ("Wait for a while\nUsage: wait <seconds>")
```
El comando es `sleep`, no `wait`. El mensaje debería decir `sleep <seconds>`.

---

### 25. `hexdump.py:5` — Mensaje de error en español
```python
raise TypeError("Los datos deben ser bytes, bytearray o str.")
```
El resto del proyecto está en inglés. Debería ser consistente.

---

### 26. `upyDesktop.py:80` — Token de autenticación hardcodeado
```python
if 'auth_token=valid_session' in cookie:
```
El token de sesión es un string fijo `"valid_session"`. Cualquiera que conozca este valor puede acceder sin autenticarse. Debería generarse un token aleatorio por sesión.

---

### 27. `upyDesktop.py:217` — Typo en comentario "distiguish"
```python
# We need to distiguish files and dirs.
```
Debería ser "distinguish".

---

### 28. `kernel.py:58` — Campo `"alias"` se crea pero nunca se usa
El sistema de alias se define en `sysconfig` pero no hay código que lo procese en `run_cmd()`. Sería útil implementarlo o eliminarlo.

---

### 29. `wait.py:11-19` — Busy-wait ineficiente
```python
while True:
    found=False
    for i in sdata.procs:
        if int(args[0]) == i.pid:
            found=True
    if found:
        sleep(0.200)
```
Se podría usar `break` al encontrar el proceso para no iterar toda la lista innecesariamente.

---

### 30. `upgrade.py:14` — `except:` bare sin tipo
```python
try:
    import urequests
    import usocket
    import ssl
except:
    print("Try atupgrade with esp-at modem instead")
```
Debería ser `except ImportError:`.

---

### 31. Seguridad — `upyDesktop.py` no valida paths del filesystem
Los handlers `fs_delete_handler`, `fs_write_handler`, etc., no verifican si el path es un archivo protegido del sistema (usando `utls.protected()`). Un usuario autenticado podría borrar `/boot.py` o `/main.py` desde la interfaz web.

---

### 32. `ps.py:10-11` — Ayuda se muestra con 1 argumento en lugar de `--h`
```python
if len(args) == 1:
    print("Show process status\nUsage: ps")
    return
```
Esto significa que `ps --h` muestra la ayuda, pero también `ps cualquiercosa`. Debería verificar `"--h" in args`.

---

### 33. `uhttpd.py:26` — `upyDesktop` puede no estar definido
```python
if hasattr(upyDesktop, 'ws_accept_callback'):
```
Si el `import upyDesktop` en la línea 18 falla (capturado por `except ImportError`), la variable `upyDesktop` no existirá y esta línea lanzará `NameError`.

**Corrección sugerida:**
```python
try:
    if hasattr(upyDesktop, 'ws_accept_callback'):
        mws.AcceptWebSocketCallback = upyDesktop.ws_accept_callback
except NameError:
    pass
```

---

### 34. `app.js:901` — Regex de highlighting puede dar falsos positivos con números
```python
if (/\d+/.test(match)) return `<span class="hl-num">${match}</span>`;
```
Esto podría colorear números dentro de identificadores como `var1` si el regex principal los captura.

---

### 35. `desktop.html:127` — Versión hardcodeada
```html
<h1>upyOS Desktop v0.4</h1>
```
La versión del desktop está hardcodeada y no se sincroniza con `sdata.version`. Debería obtenerse dinámicamente del API `/api/status`.

---

## 📋 RESUMEN

| Categoría | Cantidad |
|-----------|----------|
| 🔴 Errores (Bugs) | 13 |
| 🟡 Mejoras | 22 |
| **Total** | **35** |

### Prioridad Alta (pueden causar crashes):
- #2 — IndexError en variable expansion (`kernel.py`)
- #4 — TypeError en `ls.py` al desempaquetar
- #5 — NameError en `wifi.py` sin módulo network
- #6 — Archivo no cerrado y tipo incorrecto en `wget.py`
- #10 — Orden incorrecto `>>` vs `>` en `gpio.py`
- #33 — NameError en `uhttpd.py`

### Prioridad Media (comportamiento incorrecto):
- #1 — Alias vacíos
- #3 — String vs lista en proc.py
- #7, #8, #12 — Typos en mensajes
- #9 — IndexError en test.py
- #20 — Espacios perdidos en echo.py

### Prioridad Baja (mejoras de calidad):
- #13-35 — Mejoras de código, seguridad y mantenibilidad
