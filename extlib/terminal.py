# This file is part of the octopusLAB project
# The MIT License (MIT)
# Copyright (c) 2016-2020 Jan Copak, Petr Kracik, Vasek Chalupnicek

# from shell.terminal import printTitle

SEPARATOR_WIDTH = 50


def terminal_color(txt,col=33): # default yellow
    # 30 black / 31 red / 32 green / 33 yellow / 34 blue / 35 violet / 36 cyan 
    # 21 underline
    # print("\033[32mgreen\033[m")
    return "\033[" + str(col) + "m" + str(txt) + "\033[m"


def runningEffect(num = 16):
    from time import sleep_ms
    for ii in range(num):
        print(".",end="")
        sleep_ms(20)
    print()


def printBar(num1,num2,char="|",col1=32,col2=33):
    print("[",end="")
    print((("\033[" + str(col1) + "m" + str(char) + "\033[m")*num1),end="")
    print((("\033[" + str(col2) + "m" + str(char) + "\033[m")*num2),end="")
    print("]  ",end="")


# ---------------

def printHead(s):
    print()
    print('-' * SEPARATOR_WIDTH)
    print("[--- " + s + " ---] ")


def printTitle(t,w=SEPARATOR_WIDTH):
    print()
    print('=' * w)
    print("|",end="")
    print(t.center(w-2),end="")
    print("|")
    print('=' * w)


def printLog(i,s=""):
    print()
    print('-' * SEPARATOR_WIDTH)
    print("[--- " + str(i) + " ---] " + s)


def getUid(short = False): # full or short (5 chars: first 2 + last 3)
    import machine, ubinascii
    id = ubinascii.hexlify(machine.unique_id()).decode()
    if short:
        return id[:2]+id[-3:]
    else:
        return id


def printInfo():
    import gc #mem_free
    print("> mem_free: "+str(gc.mem_free()))
    df()


def printMachineInfo():
    import machine
    print("> machine.freq: "+str(machine.freq()))
