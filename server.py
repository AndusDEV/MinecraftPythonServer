import socket
import json
import time

HOST = '0.0.0.0'
PORT = 25565

PROTOCOL_VERSION = 767  # Minecraft 1.21
STATE_HANDSHAKE = 0
STATE_STATUS = 1
STATE_LOGIN = 2

# Encode VarInt (used mostly in packet length)
def encode_varint(value):
    out = bytearray()
    while True:
        temp = value & 0b01111111
        value >>= 7
        if value != 0:
            temp |= 0b10000000
        out.append(temp)
        if value == 0:
            break
    return out

# Decode VarInt (from the incoming data stream)
def decode_varint(sock):
    num_read = 0
    result = 0
    while True:
        byte = sock.recv(1)[0]
        result |= (byte & 0x7F) << (7 * num_read)
        num_read += 1
        if num_read > 5:
            raise ValueError("VarInt too big")
        if not (byte & 0x80):
            break
    return result

# Server status (in server list) response
def create_status_response():
    status = {
        "version": {
            "name": "Py 1.21",
            "protocol": PROTOCOL_VERSION
        },
        "players": {
            "max": 100,
            "online": 99,
            "sample": []
        },
        "description": {
            "text": "§aThis server is\nwritten in §ePython"
        }
    }

    response_json = json.dumps(status)
    encoded_json = response_json.encode('utf-8')

    # status_response packet
    packet_id = 0x00
    packet_data = encode_varint(packet_id) + encode_varint(len(encoded_json)) + encoded_json
    packet_length = encode_varint(len(packet_data))
    return packet_length + packet_data

# Ping response (X ms)
def create_pong_response(ping_payload):
    # Pong packet (followed by same ping payload)
    packet_id = encode_varint(0x01)
    return packet_id + ping_payload

# Kick packet creator
def create_kick_packet(reason):
    message = json.dumps({"text": reason})
    encoded_message = message.encode('utf-8')

    # Disconnect packet
    packet_id = 0x00
    packet_data = encode_varint(packet_id) + encode_varint(len(encoded_message)) + encoded_message
    packet_length = encode_varint(len(packet_data))
    return packet_length + packet_data

def handle_client(client_socket):
    try:
        # Handshake handling
        packet_length = decode_varint(client_socket)
        packet_id = decode_varint(client_socket)

        if packet_id == 0x00:  # Handshake packet
            protocol_version = decode_varint(client_socket)  # Protocol Version
            hostname_length = decode_varint(client_socket)
            client_socket.recv(hostname_length)  # Hostname
            client_socket.recv(2)  # Port (ignored | 2 bytes)
            next_state = decode_varint(client_socket)

            if next_state == STATE_STATUS:
                handle_status(client_socket)
            elif next_state == STATE_LOGIN:
                handle_login(client_socket)

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def handle_status(client_socket):
    try:
        # Status request
        packet_length = decode_varint(client_socket)
        packet_id = decode_varint(client_socket)

        if packet_id == 0x00:  # Status request
            # Send status response
            status_response = create_status_response()
            client_socket.send(status_response)

        # Ping request
        packet_length = decode_varint(client_socket)
        packet_id = decode_varint(client_socket)

        if packet_id == 0x01:  # Ping packet
            # Ping payload (8 bytes)
            ping_payload = client_socket.recv(8)
            if len(ping_payload) == 8:
                # Capture the time when the server received the ping
                start_time = time.time()

                # Pong response
                pong_response = create_pong_response(ping_payload)
                client_socket.send(pong_response)

                # Calculate ping time in milliseconds
                ping_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                print(f"Ping time: {ping_time:.2f} ms")

    except Exception as e:
        print(f"Error during status handling: {e}")

def handle_login(client_socket):
    try:
        # Kick player on login
        kick_reason = "§cYou were kicked by server.\n§aIt's intended though."
        kick_packet = create_kick_packet(kick_reason)
        client_socket.send(kick_packet)
    except Exception as e:
        print(f"Error during login handling: {e}")

# Main server loop
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from: {addr}")
            handle_client(client_socket)
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
