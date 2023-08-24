import gc, micropython
gc.collect()
f = gc.mem_free()
a = gc.mem_alloc()
t = f+a
p = f'({f/t*100:.2f}%)'
d={"total": t, "alloc": a, "free": f, "%": p}
print(d)

micropython.mem_info(1)