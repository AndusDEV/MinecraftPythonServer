import json

from varint import encode_varint

PROTOCOL_VERSION = 767  # Minecraft 1.21


# Server status (in server list) response
def create_status_response():
    status = {
        "version": {
            "name": "1.21",
            "protocol": PROTOCOL_VERSION
        },
        "players": {
            "max": 0,
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
    # Pong packet (followed by the same ping payload)
    packet_id = encode_varint(0x01)
    return packet_id + ping_payload


# Kick Player
def create_kick_packet(reason):
    message = json.dumps({"text": reason})
    encoded_message = message.encode('utf-8')

    packet_id = 0x00  # Disconnect packet
    packet_data = encode_varint(packet_id) + encode_varint(len(encoded_message)) + encoded_message
    packet_length = encode_varint(len(packet_data))
    return packet_length + packet_data
