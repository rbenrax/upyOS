import sys

# Current process refeference (passed in call)
proc=None

def __main__(args):
    print(f"Hello World: {args=}")
    proc.syscall.print_msg(f"Hello World from syscall: {args=}")

if __name__ == '__main__':
    __main__("a1 a 2 a3 a4 an")