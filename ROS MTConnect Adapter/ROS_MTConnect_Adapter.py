import rospy
import os
import sys
import time
from std_msgs.msg import Float64MultiArray

import std_msgs
from std_msgs.msg import String

ROBOT_ID = "dsr01"
ROBOT_MODEL = "m1509"

sys.dont_write_bytecode = True
sys.path.append(os.path.abspath((os.path.join(os.path.dirname(__file__),"../../doosan-robot/common/imp"))))

import DR_init
DR_init.__dsr__id = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL
from DSR_ROBOT import *

from mtconnect_adapter import MTConnectAdapter

def call_robot_posj_service():
    rospy.wait_for_service('/dsr01m1509/aux_control/get_current_posj')
    try:
        robot_posj_srv = rospy.ServiceProxy('/dsr01m1509/aux_control/get_current_posj', GetCurrentPosj)
        response = robot_posj_srv()
        return response.pos
    except rospy.ServiceException as e:
        rospy.logerr("Service call failed: %s", e)
        return None

def call_robot_posx_service():
    rospy.wait_for_service('/dsr01m1509/aux_control/get_current_posx')
    try:
        robot_posx_srv = rospy.ServiceProxy('/dsr01m1509/aux_control/get_current_posx', GetCurrentPosx)
        response = robot_posx_srv()
        return response.task_pos_info[0].data
    except rospy.ServiceException as e:
        rospy.logerr("Service call failed: %s", e)
        return None

def call_robot_solutionspace_service():
    rospy.wait_for_service('/dsr01m1509/aux_control/get_current_solution_space')
    try:
        robot_solutionspace_srv = rospy.ServiceProxy('/dsr01m1509/aux_control/get_current_solution_space', GetCurrentSolutionSpace)
        response = robot_solutionspace_srv()
        return response.sol_space
    except rospy.ServiceException as e:
        rospy.logerr("Service call failed: %s", e)
        return None

def call_status_service():
    rospy.wait_for_service('/dsr01m1509/system/get_robot_mode')
    try:
        robot_mode_srv = rospy.ServiceProxy('/dsr01m1509/system/get_robot_mode', GetRobotMode)
        response = robot_mode_srv()
        return response.robot_mode
    except rospy.ServiceException as e:
        rospy.logerr("Service call failed: %s", e)
        return None

if __name__ == "__main__":
    rospy.init_node('status_client_node', anonymous=True)

    # Adapter 인스턴스 생성, 실행
    adapter = MTConnectAdapter(host='127.0.0.1', port=7878)
    adapter.start()

    rate = rospy.Rate(10)  # 0.1 초에 한 번 -> 추후 프레임 검사 필수
    while not rospy.is_shutdown():
        
        posj_result = call_robot_posj_service()
        if posj_result is not None:
            adapter.update_data("DR_M_posj_jo", posj_result[0])
            adapter.update_data("DR_M_posj_j1", posj_result[1])
            adapter.update_data("DR_M_posj_j2", posj_result[2])
            adapter.update_data("DR_M_posj_j3", posj_result[3])
            adapter.update_data("DR_M_posj_j4", posj_result[4])
            adapter.update_data("DR_M_posj_j5", posj_result[5])

        posx_result = call_robot_posx_service()
        if posx_result is not None:
            adapter.update_data("DR_M_posx_X", posx_result[0])
            adapter.update_data("DR_M_posx_Y", posx_result[1])
            adapter.update_data("DR_M_posx_Z", posx_result[2])
            adapter.update_data("DR_M_posx_Rx", posx_result[3])
            adapter.update_data("DR_M_posx_Ry", posx_result[4])
            adapter.update_data("DR_M_posx_Rz", posx_result[5])

        solutionspace_result = call_robot_solutionspace_service()
        if solutionspace_result is not None:
            adapter.update_data("robot_solutionspace", solutionspace_result)

        mode_result = call_status_service()
        if mode_result is not None:
            adapter.update_data("robot_mode_id", mode_result)

        # print(posj_result)
        # print(posx_result)
        # print(solutionspace_result)
        # print(mode_result)

        rate.sleep()

    # 노드 종료 시 Adapter도 정지
    adapter.stop()
