# Copyright 2020 Petr Viktorin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

# 2020-04-29 Vasek Chalupnicek - fixing TAB and DELETE key

import sys

CSI = '\033['
MOVE_SOL = CSI + 'G'
ERASE_LINE = CSI + '2K'
TAB_SPACES = 4

def editstr(string):
    """Return edited string, or None if cancelled."""
    cursor_pos = len(string)

    def escape():
        c = sys.stdin.read(1)
        if c == '[':
            esc_bracket()
        elif c == 'O':
            c = sys.stdin.read(1)
            if c == 'H':
                home()
            if c == 'F':
                end()
            else:
                unknown('ESC O ' + repr(c))
        elif c == 'b':
            backward_word()
        elif c == 'f':
            forward_word()
        else:
            unknown('ESC ' + repr(c))

    def esc_bracket():
        c = sys.stdin.read(1)
        if ord('0') <= ord(c) <= ord('9'):
            c += sys.stdin.read(1)
            if c in ('1~', '7~'):
                home()
            elif c in ('4~', '8~'):
                end()
            elif c == '3~':
                delete()
            elif c == '1;':
                esc_bracket()
            elif c == '5C':
                forward_word()
            elif c == '5D':
                backward_word()
            else:
                unknown('ESC [ ' + repr(c))
        elif c == 'A':
            up_arrow()
        elif c == 'B':
            down_arrow()
        elif c == 'C':
            right_arrow()
        elif c == 'D':
            left_arrow()
        elif c == 'H':
            home()
        elif c == 'F':
            end()
        else:
            unknown('ESC [ ' + repr(c))

    def redraw():
        print(
            MOVE_SOL + ERASE_LINE + string + CSI + str(cursor_pos+1) + 'G',
            end=''
        )

    def home():
        nonlocal cursor_pos, string
        cursor_pos = 0

    def end():
        nonlocal cursor_pos, string
        cursor_pos = len(string)

    def backward_word():
        nonlocal cursor_pos, string
        while cursor_pos and string[cursor_pos-1] == ' ':
            cursor_pos -= 1
        while cursor_pos and string[cursor_pos-1] != ' ':
            cursor_pos -= 1

    def forward_word():
        nonlocal cursor_pos, string
        while cursor_pos < len(string) and (string+'_')[cursor_pos] == ' ':
            cursor_pos += 1
        while cursor_pos < len(string) and (string+' ')[cursor_pos] != ' ':
            cursor_pos += 1

    def delete():
        nonlocal cursor_pos, string
        if cursor_pos < len(string):
            string = string[:cursor_pos] + string[cursor_pos+1:]

    def backspace():
        nonlocal cursor_pos, string
        if cursor_pos > 0:
            cursor_pos -= 1
            string = string[:cursor_pos] + string[cursor_pos+1:]

    def right_arrow():
        nonlocal cursor_pos, string
        if cursor_pos < len(string):
            cursor_pos += 1

    def left_arrow():
        nonlocal cursor_pos, string
        if cursor_pos > 0:
            cursor_pos -= 1

    def kill_to_end():
        nonlocal cursor_pos, string
        string = string[:cursor_pos]

    def kill_to_beginning():
        nonlocal cursor_pos, string
        string = string[cursor_pos+1:]
        cursor_pos = 0

    def letter(c):
        nonlocal cursor_pos, string
        if cursor_pos == len(string):
            string += c
            cursor_pos += 1
        else:
            string = string[:cursor_pos] + c + string[cursor_pos:]
            cursor_pos += 1

    def tab():
        nonlocal cursor_pos, string
        if cursor_pos == len(string):
            string += ' ' * TAB_SPACES
            cursor_pos += TAB_SPACES
        else:
            string = string[:cursor_pos] + ' ' * TAB_SPACES + string[cursor_pos:]
            cursor_pos += TAB_SPACES

    def unknown(s):
        print(MOVE_SOL + ERASE_LINE + 'Unknown: ' + s)

    def up_arrow():
        nonlocal cursor_pos

    def down_arrow():
        nonlocal cursor_pos

    try:
        while True:
            redraw()
            c = sys.stdin.read(1)
            oc = ord(c)
            if oc == 127:
                backspace()
            elif oc == 1:
                # CTRL-A
                home()
            elif oc == 2:
                # CTRL-B
                left_arrow()
            elif oc == 3:
                # CTRL-C
                print()
                return None
            elif oc == 4:
                # CTRL-D
                delete()
            elif oc == 5:
                # CTRL-E
                end()
            elif oc == 6:
                # CTRL-F
                right_arrow()
            elif oc == 11:
                # CTRL-K
                kill_to_end()
            elif oc == 14:
                # CTRL-N
                down_arrow()
            elif oc == 16:
                # CTRL-P
                up_arrow()
            elif oc == 21:
                # CTRL-U
                kill_to_beginning()
            elif oc == 23:
                # CTRL-W
                backward_word()
            elif c in ('\r', '\n'):
                return string
            elif oc == 27:
                escape()
            elif oc == 8:
                delete()
            elif oc == 9:
                tab()
            elif oc >= 32:
                letter(c)
            else:
                unknown(repr(c))
    finally:
        print(MOVE_SOL + ERASE_LINE, end='')
