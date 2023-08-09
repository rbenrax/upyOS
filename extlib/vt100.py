import sys

def get_cursor_position():
    height=0
    width=0
    num=''

    sys.stdout.write('\x1b[6n')
    while True:
        char = sys.stdin.read(1)
        if char is 'R':
            width = int(num)
            break
        if char is '\x1b':
            width=0
            height=0
            num=''
            continue
        if char is '[':
            continue
        if char is ';':
            height=int(num)
            num=''
            continue
        num+=char
    return (width, height)

def get_terminal_size():
    # Save cursor position
    sys.stdout.write('\x1b[s')
    
    #Move cursor outside of screen
    sys.stdout.write('\x1b[999B\x1b[999C')
    (w, h) = get_cursor_position()
    
    # Restore cursor position
    sys.stdout.write('\x1b[u')

    return (w, h)
