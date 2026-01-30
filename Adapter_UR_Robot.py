# Made by KAIST 스마트생산시스템연구실
import os
import sys
import time
import math
import numpy as np

# sys.dont_write_bytecode = True
# sys.path.append(os.path.abspath((os.path.join(os.path.dirname(__file__),""))))

from rtde_control import RTDEControlInterface
from rtde_receive import RTDEReceiveInterface 
from MTConnectAdapter_Base import MTConnectAdapter

'''UR Robot RTDE Connection'''
UR_ID = []
UR_1_rtde_controller = None
UR_1_rtde_receiver = None
UR_2_rtde_controller = None
UR_2_rtde_receiver = None

try:
    UR_1_rtde_controller = RTDEControlInterface("192.168.1.101")
    UR_1_rtde_receiver = RTDEReceiveInterface("192.168.1.101")
    UR_ID.append(1)
    print("UR Robot 1")
except Exception as e:
    UR_ID.append(0)
    print(f"UR Robot 1 Not Connected")
    pass
try:
    UR_2_rtde_controller = RTDEControlInterface("192.168.1.102")
    UR_2_rtde_receiver = RTDEReceiveInterface("192.168.1.102")
    UR_ID.append(1)
    print("UR Robot 2")
except Exception as e:
    UR_ID.append(0)
    print(f"UR Robot 2 Not Connected")
    pass

def ur_robot_joint_data(ur_id):
    if ur_id == 1:
        try:
            response = UR_1_rtde_receiver.getActualQ() #getActualQd() for velocity information
            response = [(x * 180 / math.pi) for x in response]
            return [f"{value:.2f}" for value in response]
        except Exception as e:
            print(f"UR Robot 1 Joint Data Error: {e}")
            return None
    
    if ur_id == 2:
        try:
            response = UR_2_rtde_receiver.getActualQ()
            response = [(x * 180 / math.pi) for x in response]
            return [f"{value:.2f}" for value in response]
        except Exception as e:
            print(f"UR Robot 2 Joint Data Error: {e}")
            return None

def ur_robot_TCP_data(ur_id):
    if ur_id == 1:
        try:
            response = UR_1_rtde_receiver.getActualTCPPose()
            return [f"{value:.2f}" for value in response]
        except Exception as e:
            print(f"UR Robot 1 Joint Data Error: {e}")
            return None
    
    if ur_id == 2:
        try:
            response = UR_2_rtde_receiver.getActualTCPPose()
            # print(response)
            return [f"{value:.2f}" for value in response]
        except Exception as e:
            print(f"UR Robot 2 Joint Data Error: {e}")
            return None


def ur_robot_other_data(ur_id):
    if ur_id == 1:
        try:
            response = UR_1_rtde_receiver.getActualDigitalInputBits()
            input_list = [(response >> i) & 1 for i in range(8)]
            return [f"{x}" for x in input_list]
        except Exception as e:
            print(f"UR Robot 1 Joint Data Error: {e}")
            return None
    
    if ur_id == 2:
        try:
            response = UR_2_rtde_receiver.getActualDigitalInputBits()
            input_list = [(response >> i) & 1 for i in range(8)]
            return [f"{x}" for x in input_list]
        except Exception as e:
            print(f"UR Robot 2 Joint Data Error: {e}")
            return None

def update_robot_adapter(adapter, prefix, joint_data, tcp_data, other_data, prev_states):
    if joint_data is None or tcp_data is None or other_data is None:
        return
    data_map = {}
    
    for i in range(6):
        data_map[f"{prefix}_j{i}"] = joint_data[i]
    
    tcp_labels = ["X", "Y", "Z", "Rx", "Ry", "Rz"]
    for i, label in enumerate(tcp_labels):
        data_map[f"{prefix}_{label}"] = tcp_data[i]
        
    for i in range(8):
        data_map[f"{prefix}_DI_{i}"] = other_data[i]

    for key, current_val in data_map.items():
        if prev_states.get(key) != current_val:
            adapter.update_data(key, current_val)
            prev_states[key] = current_val
        

if __name__ == "__main__":
    # Adapter 인스턴스 생성, 실행
    adapter1 = MTConnectAdapter(host='127.0.0.1', port=8101)
    adapter2 = MTConnectAdapter(host='127.0.0.1', port=8102)

    adapter1.start()
    adapter2.start()
    UR_1_Previous_State = {}
    UR_2_Previous_State = {}
    
    try:
        while True:
            # start_time = time.time()
            if UR_ID[0] == 1:
                UR_1_Robot_Joint_Data = ur_robot_joint_data(1)
                UR_1_Robot_TCP_Data = ur_robot_TCP_data(1)
                UR_1_Robot_Other_Data = ur_robot_other_data(1)
                update_robot_adapter(adapter1, "UR_1", UR_1_Robot_Joint_Data, UR_1_Robot_TCP_Data, UR_1_Robot_Other_Data, UR_1_Previous_State)

            if UR_ID[1] == 1:
                # measure_time = time.time()
                UR_2_Robot_Joint_Data = ur_robot_joint_data(2)
                UR_2_Robot_TCP_Data = ur_robot_TCP_data(2)
                UR_2_Robot_Other_Data = ur_robot_other_data(2)
                update_robot_adapter(adapter2, "UR_2", UR_2_Robot_Joint_Data, UR_2_Robot_TCP_Data, UR_2_Robot_Other_Data, UR_2_Previous_State)

                # end_time = time.time()
                # print("Time Spent:", f"{end_time - measure_time:.5f}")
            time.sleep(0.008)
            # print(adapter2)
    except KeyboardInterrupt:
        print("Exited by the User")
    finally:
        adapter1.stop()
        adapter2.stop()
        print("UR Robot Adapter Executed")
