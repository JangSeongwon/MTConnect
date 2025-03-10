# ROS MTConnect Adapter 코드 
import rospy
import os
import socket
import threading, time
import sys

from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Pose
from sensor_msgs.msg import JointState

client_counter = 0
client_list = []
first_run_flag = 1
lock = threading.Lock()
event = threading.Event()
event.set()

"""
ROS 신호 Reading
"""

def callback_pos(msg):
    start = time.time()
    POS = msg.pose.position
    ORI = msg.pose.orientation
    # print('Check Subscription')
    Hapticx = POS.x
    Hapticy = POS.y
    Hapticz = POS.z
    # print('See Haptic info',Hapticx, Hapticy, Hapticz)
    
    '''Doosan Robot Home Position'''
    robot_pos = [-33.208, 426.252, -374.960, 89.988, -87.678, 0.227]
    
    '''ROS Coordinate (Hapticx = ROSx, Hapticy = ROSy, Hapticz = -ROSz)'''
    x = round(robot_pos[0] + Hapticx*1000, 1)
    y = round(robot_pos[1] + Hapticy*1000, 1)
    z = round(robot_pos[2] - Hapticz*1000, 1)

    robot_pos_c = get_current_posx(Haptic_coord)
    getfromtuple = robot_pos_c[0]
    current_x = round(getfromtuple[0], 3)
    current_y = round(getfromtuple[1], 3)
    current_z = round(getfromtuple[2], 3)

    current_Rx = round(getfromtuple[3], 3)
    current_Ry = round(getfromtuple[4], 3)
    current_Rz = round(getfromtuple[5], 3)

    eef = [x, y, z, current_Rx, current_Ry, current_Rz]
    velx=[500, 120]
    accx=[2000, 240]

    """Publish"""
    operator_trajectory = PoseStamped()
    operator_trajectory.header.stamp = rospy.Time.now()
    operator_trajectory.pose.position.x = current_x
    operator_trajectory.pose.position.y = current_y
    operator_trajectory.pose.position.z = current_z
    operator_trajectory.pose.orientation.x = current_Rx
    operator_trajectory.pose.orientation.y = current_Ry
    operator_trajectory.pose.orientation.x = current_Rz
    operator_trajectory.pose.orientation.w = 0
    # print(operator_trajectory.pose.position, operator_trajectory.pose.orientation)
    pub.publish(operator_trajectory)   

    """오차 범위"""
    if (abs(current_x - x) < 0.5) and (abs(current_y - y) < 0.5) and (abs(current_z - z) < 0.5):
        end1 = time.time()
        # print("No Move", end1-start)
        return
    else:
        amovel(eef, velx, accx, ref = Haptic_coord)
        end2 = time.time()
        print(end2-start)
    
def callback_ori(msg):
    start = time.time()
    ORI = msg.orientation
    robot_home_ori = [89.988, -87.678, 0.227]
    robot_pos_current = get_current_posx()
    getfromtuple = robot_pos_current[0]
    # print('Current Robot POS = ', robot_pos_fixed)

    '''
    Haptic Input Into New ROS Coordinates
    Haptic X: -130도~60도, Haptic Z: -150도~160도
    '''
    sensitivity_x = 5
    sensitivity_z = 5
    Haptic_Rx = (ORI.x / sensitivity_x)
    # Haptic_Ry = ORI.y
    Haptic_Rz = (ORI.z / sensitivity_z)
    Rx = round(robot_home_ori[0] + Haptic_Rz, 3)
    Ry = round(robot_home_ori[1] + Haptic_Rx, 3)

    Rx_c = robot_pos_current[0][3] 
    Ry_c = robot_pos_current[0][4]
    Rz_c = robot_pos_current[0][5]
    # print('Haptic Orientaion Input : ', Rx, Ry, Rz)

    Fixed_x = round(getfromtuple[0], 3)
    Fixed_y = round(getfromtuple[1], 3)
    Fixed_z = round(getfromtuple[2], 3)

    eef = [Fixed_x, Fixed_y, Fixed_z, Rx, Ry, Rz_c]
    velx=[500, 120]
    accx=[2000, 240]

    """Publish"""
    operator_trajectory = PoseStamped()
    operator_trajectory.header.stamp = rospy.Time.now()
    operator_trajectory.pose.position.x = Fixed_x
    operator_trajectory.pose.position.y = Fixed_y
    operator_trajectory.pose.position.z = Fixed_z
    operator_trajectory.pose.orientation.x = Rx_c
    operator_trajectory.pose.orientation.y = Ry_c
    operator_trajectory.pose.orientation.z = Rz_c
    operator_trajectory.pose.orientation.w = 0
    # print(operator_trajectory.pose.position, operator_trajectory.pose.orientation)
    pub.publish(operator_trajectory) 
    
    if (abs(Rx_c - Rx) < 0.1) and (abs(Ry_c - Ry) < 0.1):
        end1 = time.time()
        # print(end1-start)
        return
    else:
        amovel(eef, velx, accx, ref = Haptic_coord)
        # robot_pos_check = get_current_posx(Haptic_coord)
        # print('Haptic Orientaion Input', 'x : 90 ', Rx, 'y : -90 ', Ry, 'z : 0 ', Rz)
        # print('Current Robot ORI = ', robot_pos_check[0][3], robot_pos_check[0][4], robot_pos_check[0][5])
        end = time.time()
        print(end-start)  

    return

def call_service():
    rospy.init_node('service_client')
    
    rospy.wait_for_service('/your_service_name')
    try:
        service_proxy = rospy.ServiceProxy('/your_service_name', Trigger)
        response = service_proxy()
        rospy.loginfo(f"Response: {response.success}, Message: {response.message}")
    except rospy.ServiceException as e:
        rospy.logerr(f"Service call failed: {e}")

if __name__ == "__main__":
    
    rospy.init_node('Haptic')
    call_service()

    while not rospy.is_shutdown():
        rospy.Subscriber(name = "/HapticInfo", data_class = PoseStamped, callback = callback_pos)
        rospy.Subscriber(name = "/HapticOri", data_class = Pose, callback = callback_ori)
        r = rospy.Rate(50)
        rospy.spin()


"""
Adapter Connection
본 프로그램이 돌아가는 PC의 IP address, Port를 입력
"""
HOST = 'localhost'
PORT = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create  #AF_INET: IPv4, SOCK_STREAM: 해당 소켓에 TCP/IP를 받겠다
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #포트를 사용중일때 에러를 해결

"""Binding to the local port/host"""
try:
    s.bind((HOST, PORT)) #method of Python's socket class assigns an IP address and a port number to a socket instance.
except socket.error as msg:
    print ('Bind failed. Error Code : ' + str(msg)) 
    sys.exit() #print message if s.bind is unsuccessful

"""Start Listening to Socket for Clients"""
s.listen(5) #s.listen to listen to Socket for Clients. The "5" stands for how many incoming connections we're willing to queue before denying any more.

def thread_list_empty():
    global client_list, client_counter

    while True:
        try:
            if client_counter == 0 and first_run_flag == 0 and client_list != []:
                print("%d Clients Active" % client_counter)
                print("Clearing All threads....")
                for index, thread in enumerate(client_list):
                    thread.join()
                client_list = []
        except:
            print("Invalid Client List Deletion")

        if not event.is_set():
            print("Closing thread_list_empty thread..")
            return
        
def ROS_adapter():

    global switch_signal, combined_plc_signal, switch_signal_previous, format_switch_signal
    while True:
        switch_signal_previous = "None"
        updated = False
        out_initial = 'No Press'
        plc_signal = ''
        try:
            switch_signal = ""
            # PLC에서 Holding Register 0번 주소 (D100) 읽기
            # count=1 은 16bit로 1개 WORD
            try:
                switch_signal = client.read_holding_registers( address=100, count=1, slave=1)
                # print('Read', switch_signal)
                if switch_signal.isError():
                    print("Reading Fail:", switch_signal)
                # else:
                #     print("PLC Data read:", switch_signal.registers)
            except:
                switch_signal = 'No Press'

            if switch_signal.registers != switch_signal_previous:
                format_switch_signal = switch_signal.registers[0]
                updated = True
                plc_signal += "|Switch|" + str(format_switch_signal)
                switch_signal_previous = format_switch_signal
        
        except Exception as ex:
            print("No signal from PLC " + ex)
            time.sleep(2) 
        
        time.sleep(0.1)
        if not updated:
            pass
        combined_plc_signal = '\r\n' + datetime.datetime.now().isoformat() + 'Z' + plc_signal
                
        if not event.is_set():
            print("Closing PLC thread..")
            return
        

class NewClientThread(threading.Thread):
    # init method called on thread object creation,
    def __init__(self, conn, string_address):
        threading.Thread.__init__(self)
        self.connection_object = conn
        self.client_ip = string_address

    # run method called on .start() execution
    def run(self):
        global client_counter, combined_plc_signal
        global lock
        while True:
            try:
                #print("Sending data to Client {} in {}".format(self.client_ip, self.getName()))
                out = combined_plc_signal
                print("OUT: "+ out)
                self.connection_object.sendall(out.encode())
                time.sleep(1)

            except Exception as e:
                lock.acquire()
                try:
                    print("Error", e)
                    client_counter = client_counter - 1
                    print("Connection disconnected for ip {} ".format(self.client_ip))
                    break
                finally:
                    lock.release()

            if not event.is_set():
                print("Closing NewClientThread thread..")
                return

"""Starts From Here"""
t1 = threading.Thread(target=thread_list_empty)
t2 = threading.Thread(target=plc_adapter)
# t1.setDaemon(True)
# t2.setDaemon(True)
t1.start()
t2.start()
time.sleep(2)
print("setup")

while event.is_set():

    if first_run_flag == 1:
        print("Listening to Port: %d...." % PORT)

    try:
        conn, addr = s.accept()
        lock.acquire()
        client_counter = client_counter + 1
        first_run_flag = 0
        print("Accepting Comm From:" + " " + str(addr))
        new_Client_Thread = NewClientThread(conn, str(addr))
        # new_Client_Thread.setDaemon(True)
        client_list.append(new_Client_Thread)
        print("Client list:", client_list)
        new_Client_Thread.start()
        lock.release()

    except KeyboardInterrupt:
        print("Ending Connection")
        event.clear()
        break




