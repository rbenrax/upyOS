import sys
import utime

# Current process refeference (passed in call)
proc=None

def __main__(args):
    print(f"Hello World: {args=}")
    proc.syscall.print_msg(f"Hello World from syscall: {args=}")
    
    for i in range(50):
        if proc and proc.sts=="S": break # if Thread, stop instruction
        
        if proc.sts=="H":
            utime.sleep(1)
            continue
        
        print(i)
        utime.sleep(2)

if __name__ == '__main__':
    __main__("a1 a 2 a3 a4 an")