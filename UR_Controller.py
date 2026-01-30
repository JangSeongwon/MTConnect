# Made by KAIST 스마트생산시스템연구실
import os
import sys
import time
import math
import numpy as np

# sys.dont_write_bytecode = True
# sys.path.append(os.path.abspath((os.path.join(os.path.dirname(__file__),""))))

from rtde_receive import RTDEReceiveInterface 
from rtde_control import RTDEControlInterface

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

def MoveJ(robot):
    print("\n[Joint Control] 입력 예시 (단위: 도): 0, 0, 0, 0, 0, 0")
    user_input = input("6개 조인트 각도를 입력하세요: ")
    try:
        joints = [float(x.strip()) * math.pi / 180.0 for x in user_input.split(',')]
        if len(joints) != 6:
            raise ValueError("값을 다시 입력하세요")
        
        if robot == '1':
            UR_1_rtde_controller.moveJ(joints, speed = 0.2, acceleration = 0.2, asynchronous=False)
        elif robot == '2':
            UR_2_rtde_controller.moveJ(joints, speed = 0.2, acceleration = 0.2, asynchronous=False)

        print("동작 완료")
    except Exception as e:
        print(f"Invalid Input: {e}")

def MoveL(robot):
    print("\n[Pose Control] 입력 예시 (단위: m, rad): 0.4, -0.2, 0.3, 3.14, 0, 0")
    user_input = input("TCP 좌표(X,Y,Z,Rx,Ry,Rz)를 입력하세요: ")
    try:
        pose = [float(x.strip()) for x in user_input.split(',')]
        if len(pose) != 6:
            raise ValueError("값을 다시 입력하세요")
        
        if robot == '1':
            UR_1_rtde_controller.moveL(pose, speed = 0.2, acceleration = 0.2, asynchronous=False)
        elif robot == '2':
            UR_2_rtde_controller.moveL(pose, speed = 0.2, acceleration = 0.2, asynchronous=False)

        print("동작 완료")
    except Exception as e:
        print(f"Invalid Input: {e}")

if __name__ == "__main__":
    while True:
        print("-------------UR로봇 RTDE 제어-------------")
        print("1: UR 로봇 1호")
        print("2: UR 로봇 2호")
        print("q: Quit")
        user_selected_robot = input("로봇 선택 후 Enter").lower()
        if user_selected_robot == '1':
            print("1: MoveJ")
            print("2: MoveL")
            print("q: Quit")
            user_called_function = input("함수 선택").lower()
            robot = '1'

            if user_called_function == '1':
                MoveJ(robot)
            elif user_called_function == '2':
                MoveL(robot)
            elif user_called_function == 'q':
                break
            else:
                print("Unknown Command.")

        elif user_selected_robot == '2':
            print("1: MoveJ")
            print("2: MoveL")
            print("q: Quit")
            user_called_function = input("함수 선택 후 Enter").lower()
            robot = '2'

            if user_called_function == '1':
                MoveJ(robot)
            elif user_called_function == '2':
                MoveL(robot)
            elif user_called_function == 'q':
                break
            else:
                print("Unknown Command.")
        else:
            print("다시 선택하세요")  

    RTDEControlInterface.stopScript()

