#!/usr/bin/env python3

# import sysfile:///home/jsw/UR5_RTDE/UR5_RDTE_Record%20(Controller_Logic).py
# print(sys.executable)
# print(sys.path)

from rtde_control import RTDEControlInterface
import rtde_receive
import time
import math
import sys
import numpy as np

rtde_cd = RTDEControlInterface("192.168.1.102")
rtde_receiver = rtde_receive.RTDEReceiveInterface("192.168.1.102")

target_q1 = [-math.radians(90), -math.radians(90), 0, 0, 0, 0]
target_q2 = [-math.radians(0), -math.radians(90), 0, 0, 0, 0]
clock = 0

while True:
    funcs = dir(rtde_receiver)
    tool_funcs = [f for f in funcs if 'Tool' in f]
    print("사용 가능한 툴 관련 함수 리스트:", tool_funcs)

    see_joints = rtde_receiver.getActualQ()
    see_vel = rtde_receiver.getActualQd()
    see_acc = rtde_receiver.getActualTCPSpeed()

    joint_byte = np.array([see_joints])
    vel_byte = np.array([see_vel])
    acc_byte = np.array([see_acc])

    io_data = rtde_receiver.getActualDigitalInputBits()
    io_data = np.array([io_data])
    print("I/O :", io_data.dtype, io_data.itemsize, io_data.nbytes)
    port_number = 0
    is_on = bool(io_data & (1 << port_number))
    print(f"{port_number}번 포트 상태: {is_on}")

    io_data1 = rtde_receiver.getActualDigitalOutputBits()
    io_data1 = np.array([io_data1])
    print("I/O :", io_data1.dtype, io_data1.itemsize, io_data1.nbytes)
    port_number1 = 0
    is_on1 = bool(io_data1 & (1 << port_number1))
    print(f"{port_number1}번 포트 상태: {is_on1}")

    print("Joints Type (rad): ", joint_byte.dtype, joint_byte.itemsize, joint_byte.nbytes)
    print("Vel Type: ", vel_byte.dtype, vel_byte.itemsize, vel_byte.nbytes)
    print("Acc Type: ", acc_byte.dtype, acc_byte.itemsize, acc_byte.nbytes)
    print(rtde_receiver.getActualDigitalInputBits())

    time.sleep(0.3)

    rtde_cd.moveJ(target_q1, speed = math.radians(90), acceleration = math.radians(90)) 
    break


del rtde_cd

# while True:
#     time.sleep(0.3)

#     rtde_cd.moveJ(target_q1, speed = math.radians(90), acceleration = math.radians(90)) 

#     time.sleep(0.3)

#     rtde_cd.moveJ(target_q2, speed = math.radians(90), acceleration = math.radians(360)) 

#     clock += 1
#     print(clock)
#     if clock == 1:
#         break
# del rtde_cd

