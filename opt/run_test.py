import sdata
import sys

# The user space functions can avoid module being removed (passed in call)
rmmod=False

# The user space functions can call system funcions by syscall reference (passed in call)
syscall=None

def __main__(args):
    print(f"Hello World: {args=}")
    syscall.print_msg(f"Hello World from syscall: {args=}")

if __name__ == '__main__':
    __main__("a1 a 2 a3 a4 an")