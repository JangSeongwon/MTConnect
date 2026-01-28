
import os
import sys
import time
import math

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
            response = UR_1_rtde_receiver.getActualQ()
            return [f"{value:.2f}" for value in response]
        except Exception as e:
            print(f"UR Robot 1 Joint Data Error: {e}")
            return None
    
    if ur_id == 2:
        try:
            response = UR_2_rtde_receiver.getActualQ()
            print(response)
            return [f"{value:.2f}" for value in response]
        except Exception as e:
            print(f"UR Robot 2 Joint Data Error: {e}")
            return None
    
if __name__ == "__main__":

    # Adapter 인스턴스 생성, 실행
    adapter1 = MTConnectAdapter(host='127.0.0.1', port=8101)
    adapter2 = MTConnectAdapter(host='127.0.0.1', port=8102)

    adapter1.start()
    adapter2.start()

    try:
        while True:
            start_time = time.time()
            if UR_ID[0] == 1:
                UR_1_Robot_Joint_Data = ur_robot_joint_data(1)
                if UR_1_Robot_Joint_Data is not None:
                    adapter1.update_data("UR_1_j0", UR_1_Robot_Joint_Data[0])
                    adapter1.update_data("UR_1_j1", UR_1_Robot_Joint_Data[1])
                    adapter1.update_data("UR_1_j2", UR_1_Robot_Joint_Data[2])
                    adapter1.update_data("UR_1_j3", UR_1_Robot_Joint_Data[3])
                    adapter1.update_data("UR_1_j4", UR_1_Robot_Joint_Data[4])
                    adapter1.update_data("UR_1_j5", UR_1_Robot_Joint_Data[5])

            if UR_ID[1] == 1:
                UR_2_Robot_Joint_Data = ur_robot_joint_data(2)
                if UR_2_Robot_Joint_Data is not None:
                    adapter2.update_data("UR_2_j0", UR_2_Robot_Joint_Data[0])
                    adapter2.update_data("UR_2_j1", UR_2_Robot_Joint_Data[1])
                    adapter2.update_data("UR_2_j2", UR_2_Robot_Joint_Data[2])
                    adapter2.update_data("UR_2_j3", UR_2_Robot_Joint_Data[3])
                    adapter2.update_data("UR_2_j4", UR_2_Robot_Joint_Data[4])
                    adapter2.update_data("UR_2_j5", UR_2_Robot_Joint_Data[5])
            time.sleep(0.005)

            print(adapter2)
    except KeyboardInterrupt:
        print("Exited by the User")
    finally:
        adapter1.stop()
        adapter2.stop()
        print("UR Robot Adapter Executed")
