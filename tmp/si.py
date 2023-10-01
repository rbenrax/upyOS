# gc
import gc
gc.collect()
f = gc.mem_free()
a = gc.mem_alloc()
t = f+a
p = f'({f/t*100:.2f}%)'
d={"total": t, "alloc": a, "free": f, "%": p}
print(d)

# micropython
import micropython
micropython.mem_info()

# platform
import uplatform
dir(uplatform)
print(f"{uplatform.libc_ver()=}")
print(f"{uplatform.platform()=}")
print(f"{uplatform.python_compiler()=}")

# sys
import sys
print(f"{sys.byteorder=}")
print(f"{sys.implementation=}")
print(f"{sys.maxsize=}")
print(f"{sys.modules=}")
print(f"{sys.path=}")
print(f"{sys.platform=}")
print(f"{sys.version=}")
print(f"{sys.version_info=}")
