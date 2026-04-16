import airsim
import time
import json

# SCALING: Drone-scale physics to Mach-speed Tactical profiles
# 121m ground * 200 = 24,200ft starting altitude
ALTITUDE_SCALING_FACTOR = 200  
# 10m/s drone speed * 40 = ~400 knots (Mach 0.6)
SPEED_SCALING_FACTOR = 40      

def execute_flight_plan():
    client = airsim.MultirotorClient()
    client.confirmConnection()
    
    # 1. Script takes control
    client.enableApiControl(True)
    client.armDisarm(True)
    
    print("[INFO] Initiating Auto-Takeoff...")
    client.takeoffAsync().join()
    
    print("[INFO] Executing Autonomous Flight Plan (Vector: North-East, Climbing)")
    # 2. Command the continuous flight vector
    client.moveByVelocityAsync(vx=10, vy=5, vz=-2, duration=600)
    
    return client

def generate_tactical_telemetry(client):
    state = client.getMultirotorState()
    gps_data = client.getGpsData().gnss.geo_point
    velocity_ms = state.kinematics_estimated.linear_velocity.get_length()

    spoofed_data = {
        "platform": "EA-18G Growler",
        "callsign": "SABER-01",
        "track_number": "JU00127",
        "lat": gps_data.latitude,
        "lon": gps_data.longitude,
        "alt_msl": gps_data.altitude * ALTITUDE_SCALING_FACTOR,
        "velocity_kts": velocity_ms * SPEED_SCALING_FACTOR,
        "timestamp": time.time()
    }
    return spoofed_data

if __name__ == "__main__":
    client = execute_flight_plan()

    try:
        while True:
            telemetry = generate_tactical_telemetry(client)
            print(f"  > [AUTO-FLIGHT] Alt: {telemetry['alt_msl']:,.0f}ft | Spd: {telemetry['velocity_kts']:.1f}kts")
            
            with open("live_mids_stream.json", "w") as f:
                json.dump(telemetry, f)
                
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[STOP] Halting flight plan...")
        client.hoverAsync().join()
        client.armDisarm(False)
        client.enableApiControl(False)