# Encode VarInt (used mostly in packet length)
def encode_varint(value):
    buffer = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            byte |= 0x80
        buffer.append(byte)
        if not value:
            break
    return bytes(buffer)


# Decode VarInt (from the incoming data)
def decode_varint(sock):
    value = 0
    shift = 0
    while True:
        byte = sock.recv(1)
        if len(byte) == 0:
            raise Exception("Socket closed unexpectedly.")
        byte = byte[0]
        value |= (byte & 0x7F) << shift
        shift += 7
        if byte & 0x80 == 0:
            break
        if shift > 35:
            raise Exception("Varint is too long.")
    return value

