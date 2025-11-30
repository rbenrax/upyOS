def hexdump(data):
    if isinstance(data, str):
        data = data.encode('utf-8')  # Asegurarse de que sea bytes
    elif not isinstance(data, (bytes, bytearray)):
        raise TypeError("Los datos deben ser bytes, bytearray o str.")

    offset = 0
    length = len(data)

    while offset < length:
        chunk = data[offset:offset + 16]
        hex_part = ''
        ascii_part = ''

        for i in range(16):
            if i < len(chunk):
                b = chunk[i]
                hex_part += f'{b:02x} '
                if 32 <= b <= 126:
                    ascii_part += chr(b)
                else:
                    ascii_part += '.'
            else:
                hex_part += '   '

        print(f'{offset:08x}  {hex_part} |{ascii_part}|')
        offset += 16

def __main__(args):
    doc = """
    hexdump
    Usage: hexdump <file> 
    """    
    if len(args) == 0 or "--h" in args:
        print(doc)
        return

    with open(args[0], 'rb') as f:
        data = f.read()
    hexdump(data)
