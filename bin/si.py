def __main__(args):
    """Show general system information"""
    
    # gc
    import gc
    gc.collect()
    f = gc.mem_free()
    a = gc.mem_alloc()
    t = f+a
    p = f'({f/t*100:.2f}%)'
    print(f"{gc.collect()=} Total: {t} Alloc: {a} Free: {f} %: {p} {gc.threshold()=}")
    print()

    # platform
    import uplatform
    dir(uplatform)
    print(f"{uplatform.libc_ver()=}")
    print(f"{uplatform.platform()=}")
    print(f"{uplatform.python_compiler()=}")
    print()

    # sys
    import sys
    #print(f"{sys.argv}")
    print(f"{sys.byteorder=}")
    print(f"{sys.implementation=}")
    print(f"{sys.maxsize=}")
    print(f"{sys.modules=}")
    print(f"{sys.path=}")
    print(f"{sys.platform=}")
    print(f"{sys.version=}")
    print(f"{sys.version_info=}")
    print()

    # sys
    import os
    print(f"{os.uname()=}")
    print(f"{os.statvfs("/")=}")
    print()

    # micropython
    import micropython
    print(f"{micropython.opt_level()=}")
    print(f"{micropython.stack_use()=}")
    print(f"{micropython.qstr_info(1)=}")
    print(f"{micropython.mem_info(1)=}")
    print()

