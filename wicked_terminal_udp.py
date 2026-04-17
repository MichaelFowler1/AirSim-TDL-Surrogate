import socket
import struct
import os
import sys
from datetime import datetime

# UDP Configuration
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

def start_decoding_engine():
    # Create and bind the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((UDP_IP, UDP_PORT))
    except Exception as e:
        print(f"[ERROR] Port {UDP_PORT} is blocked: {e}")
        sys.exit(1)

    print("=== WICKED DECODING ENGINE: VERSION 2.0 (BINARY) ===")
    print(f"[LISTENING] Monitoring UDP Port {UDP_PORT} for J-Series packets...")

    try:
        while True:
            # Receive 8 bytes (the size of our 'ff' float payload)
            data, addr = sock.recvfrom(8) 
            
            # DECODING LOGIC
            # This is where we unpack the raw binary back into human-readable data
            alt, spd = struct.unpack('!ff', data)
            
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"=== TACTICAL DISPLAY: SABER-01 [LINK ACTIVE] ===")
            print(f"Last Packet From: {addr[0]}:{addr[1]}")
            print(f"System Time:      {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
            print("-" * 50)
            print(f"ALTITUDE: {alt:,.2f} ft")
            print(f"VELOCITY: {spd:.2f} kts")
            print("-" * 50)
            print("DECODE STATUS: SUCCESS")
            print("BUFFER STATE:  CLEAN")
            
    except KeyboardInterrupt:
        print("\n[STOP] Terminal Offline.")

if __name__ == "__main__":
    start_decoding_engine()