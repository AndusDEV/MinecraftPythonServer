import socket
from varint import decode_varint
from packets import create_status_response, create_pong_response, create_kick_packet

HOST = '0.0.0.0'
PORT = 25565

STATE_HANDSHAKE = 0
STATE_STATUS = 1
STATE_LOGIN = 2


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
                # Pong response
                pong_response = create_pong_response(ping_payload)
                client_socket.send(pong_response)

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