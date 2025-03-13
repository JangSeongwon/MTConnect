import rospy
import os
import sys
import time
from std_msgs.msg import Float64MultiArray

import std_msgs
from std_msgs.msg import String

sys.dont_write_bytecode = True
sys.path.append(os.path.abspath((os.path.join(os.path.dirname(__file__),"../../doosan-robot/common/imp"))))

# import DR_init
# DR_init.__dsr__id = ROBOT_ID
# DR_init.__dsr__model = ROBOT_MODEL
from DSR_ROBOT import *

from mtconnect_adapter import MTConnectAdapter

def call_M1013_posj_service():
    rospy.wait_for_service('/dsr01m1013/aux_control/get_current_posj')
    try:
        robot_posj_srv = rospy.ServiceProxy('/dsr01m1013/aux_control/get_current_posj', GetCurrentPosj)
        response = robot_posj_srv()
        return response.pos
    except rospy.ServiceException as e:
        rospy.logerr("Service call failed: %s", e)
        return None

def call_A0912_posj_service():
    rospy.wait_for_service('/dsr01a0912/aux_control/get_current_posj')
    try:
        robot_posj_srv = rospy.ServiceProxy('/dsr01a0912/aux_control/get_current_posj', GetCurrentPosj)
        response = robot_posj_srv()
        return response.pos
    except rospy.ServiceException as e:
        rospy.logerr("Service call failed: %s", e)
        return None

def call_M1013_posx_service():
    rospy.wait_for_service('/dsr01m1013/aux_control/get_current_posx')
    try:
        robot_posx_srv = rospy.ServiceProxy('/dsr01m1013/aux_control/get_current_posx', GetCurrentPosx)
        response = robot_posx_srv()
        return response.task_pos_info[0].data
    except rospy.ServiceException as e:
        rospy.logerr("Service call failed: %s", e)
        return None

def call_A0912_posx_service():
    rospy.wait_for_service('/dsr01a0912/aux_control/get_current_posx')
    try:
        robot_posx_srv = rospy.ServiceProxy('/dsr01a0912/aux_control/get_current_posx', GetCurrentPosx)
        response = robot_posx_srv()
        return response.task_pos_info[0].data
    except rospy.ServiceException as e:
        rospy.logerr("Service call failed: %s", e)
        return None    

def call_M1013_solutionspace_service():
    rospy.wait_for_service('/dsr01m1013/aux_control/get_current_solution_space')
    try:
        robot_solutionspace_srv = rospy.ServiceProxy('/dsr01m1013/aux_control/get_current_solution_space', GetCurrentSolutionSpace)
        response = robot_solutionspace_srv()
        return response.sol_space
    except rospy.ServiceException as e:
        rospy.logerr("Service call failed: %s", e)
        return None

def call_A0912_solutionspace_service():
    rospy.wait_for_service('/dsr01a0912/aux_control/get_current_solution_space')
    try:
        robot_solutionspace_srv = rospy.ServiceProxy('/dsr01a0912/aux_control/get_current_solution_space', GetCurrentSolutionSpace)
        response = robot_solutionspace_srv()
        return response.sol_space
    except rospy.ServiceException as e:
        rospy.logerr("Service call failed: %s", e)
        return None

def call_M1013_status_service():
    rospy.wait_for_service('/dsr01m1013/system/get_robot_mode')
    try:
        robot_mode_srv = rospy.ServiceProxy('/dsr01m1013/system/get_robot_mode', GetRobotMode)
        response = robot_mode_srv()
        return response.robot_mode
    except rospy.ServiceException as e:
        rospy.logerr("Service call failed: %s", e)
        return None
    
def call_A0912_status_service():
    rospy.wait_for_service('/dsr01a0912/system/get_robot_mode')
    try:
        robot_mode_srv = rospy.ServiceProxy('/dsr01a0912/system/get_robot_mode', GetRobotMode)
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
        
        """Joint Values of Doosan robot M1013 / A0912"""
        M_posj_result = call_M1013_posj_service()
        if M_posj_result is not None:
            adapter.update_data("M1013_j0", M_posj_result[0])
            adapter.update_data("M1013_j1", M_posj_result[1])
            adapter.update_data("M1013_j2", M_posj_result[2])
            adapter.update_data("M1013_j3", M_posj_result[3])
            adapter.update_data("M1013_j4", M_posj_result[4])
            adapter.update_data("M1013_j5", M_posj_result[5])

        A_posj_result = call_A0912_posj_service()
        if A_posj_result is not None:
            adapter.update_data("A0912_j0", A_posj_result[0])
            adapter.update_data("A0912_j1", A_posj_result[1])
            adapter.update_data("A0912_j2", A_posj_result[2])
            adapter.update_data("A0912_j3", A_posj_result[3])
            adapter.update_data("A0912_j4", A_posj_result[4])
            adapter.update_data("A0912_j5", A_posj_result[5])

        """Pose Values of Doosan robot M1013 / A0912"""
        M_posx_result = call_M1013_posx_service()
        if M_posx_result is not None:
            adapter.update_data("M1013_X", M_posx_result[0])
            adapter.update_data("M1013_Y", M_posx_result[1])
            adapter.update_data("M1013_Z", M_posx_result[2])
            adapter.update_data("M1013_Rx", M_posx_result[3])
            adapter.update_data("M1013_Ry", M_posx_result[4])
            adapter.update_data("M1013_Rz", M_posx_result[5])

        A_posx_result = call_A0912_posx_service()
        if A_posx_result is not None:
            adapter.update_data("A0912_X", A_posx_result[0])
            adapter.update_data("A0912_Y", A_posx_result[1])
            adapter.update_data("A0912_Z", A_posx_result[2])
            adapter.update_data("A0912_Rx", A_posx_result[3])
            adapter.update_data("A0912_Ry", A_posx_result[4])
            adapter.update_data("A0912_Rz", A_posx_result[5])

        M_solutionspace_result = call_M1013_solutionspace_service()
        if M_solutionspace_result is not None:
            adapter.update_data("M1013_solutionspace", M_solutionspace_result)
        
        A_solutionspace_result = call_A0912_solutionspace_service()
        if A_solutionspace_result is not None:
            adapter.update_data("A0912_solutionspace", A_solutionspace_result)

        M_mode_result = call_M1013_status_service()
        if M_mode_result is not None:
            adapter.update_data("M1013_mode_id", M_mode_result)

        A_mode_result = call_A0912_status_service()
        if A_mode_result is not None:
            adapter.update_data("A0912_mode_id", A_mode_result)

        # print(A_posj_result)
        # print(A_posx_result)
        # print(A_solutionspace_result)
        # print(A_mode_result)

        rate.sleep()

    # 노드 종료 시 Adapter도 정지
    adapter.stop()
