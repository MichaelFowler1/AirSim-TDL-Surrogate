import airsim
import struct
import socket
import sys

# UDP Configuration
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def run_udp_spoofer():
    client = airsim.MultirotorClient(timeout_value=5)
    try:
        print("[DEBUG] Attempting to shake hands with AirSim...")
        client.confirmConnection()
        
        # --- FLIGHT AUTHORIZATION BLOCK ---
        print("[FLIGHT] Requesting API Control...")
        client.enableApiControl(True)
        
        print("[FLIGHT] Arming Motors...")
        client.armDisarm(True)
        
        print("[FLIGHT] Taking off...")
        client.takeoffAsync().join() 
        
        # --- THE STEEP CLIMB OUT ---
        # Instead of going straight up, we push forward (Vx=15) and up (Vz=-15) 
        # at the same time for 4 seconds. This creates a realistic, aggressive takeoff angle.
        print("[FLIGHT] Executing steep angled climb to clear obstacles...")
        client.moveByVelocityAsync(15, 0, -15, 4).join()
        
        print("[DEBUG] Obstacles cleared. Flight Active. Beginning Binary Stream...")
    except Exception as e:
        print(f"\n[ERROR] Flight Initialization Failed: {e}")
        print("Make sure Blocks.exe is running and you clicked 'No' for the Multirotor prompt.")
        sys.exit(1)

    print(f"[CONMS] Initializing Binary Stream on {UDP_IP}:{UDP_PORT}...")
    print("[INFO] Protocol: WICKED-BIT-STREAM (Big-Endian)")

    try:
        while True:
            # --- THE AFTERBURNER GLIDE ---
            # (Vx=20, Vy=0, Vz=-5, Duration=1)
            # Levels out slightly, moving 4x faster forward, and climbing steadily
            client.moveByVelocityAsync(20, 0, -5, 1).join()
            
            state = client.getMultirotorState()
            
            # Scale to Growler tactical levels
            alt = abs(state.kinematics_estimated.position.z_val) * 10
            spd = abs(state.kinematics_estimated.linear_velocity.x_val) * 20

            # BINARY PACKING (8 bytes total)
            payload = struct.pack('!ff', alt, spd)
            
            sock.sendto(payload, (UDP_IP, UDP_PORT))
            
            print(f"\r[SEND] Tx Packet: {len(payload)} bytes | Alt: {alt:,.2f} ft | Spd: {spd:.2f} kts", end="")
            
    except KeyboardInterrupt:
        print("\n[STOP] Landing and Disabling API...")
        client.landAsync().join()
        client.armDisarm(False)
        client.enableApiControl(False)
        print("[STOP] UDP Spoofer Offline.")

if __name__ == "__main__":
    run_udp_spoofer()