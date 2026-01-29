import time
from RobotSensorInterface import RobotSensorInterfaceBridge

"""
Example usage:

- Start the bridge.
- Periodically read data_sub (robot pose and joints).
- Optionally update data_pub with corrections.
- Press Ctrl+C to stop; the bridge will send a final STOP_RSI=1 reply.
"""
bridge = RobotSensorInterfaceBridge() # you may change the IP and port.
bridge.start()

print(f"START")

state = bridge.get_data_sub() # You can access the latest robot data safely
print(f"[MAIN] IPOC={state['ipoc']} "
        f"X={state['X']:.2f} Y={state['Y']:.2f} Z={state['Z']:.2f}")

# print("TCP MOVING TEST")
# a = 0
# while True:
#     bridge.set_data_pub(X=0.0, Y=0.0, Z=0.01 * a) # Robot will move 0.0001[m] in 4ms to X-direction
#     a += 1
#     time.sleep(1)

print("JOINT DATA TEST")
print("[MAIN] Press Ctrl+C to stop data collection.")
x = []
while True:
    try:
        state = bridge.get_data_sub()
        x.append(state["X"])
        time.sleep(1.0) 
    except KeyboardInterrupt:
        print("[MAIN] KeyboardInterrupt received. Requesting stop...")
    finally:
        print("robot Cartesian x data:", x)
        break

bridge.stop() # you should call stop() to ensure proper cleanup; kill packet for KUKA, threading
