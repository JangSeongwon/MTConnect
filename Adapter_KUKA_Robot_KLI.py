# KUKA 로봇 KLI통신 기반 Adapter
# 컨트롤러 내부 .src .xml 수정 필요

import socket
import xml.etree.ElementTree as ET
from MTConnectAdapter_Base import MTConnectAdapter

HOST = '172.31.1.147'
PORT = 59152

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f'Server is listening on {HOST}:{PORT}')
print('Waiting for connect...')
client_socket, client_addr = server_socket.accept()
print(f'Connected by {client_addr}')

def update_robot_adapter(adapter, prefix, joint_data, tcp_data, other_data, prev_states):
    if joint_data is None or tcp_data is None or other_data is None:
        return
    data_map = {}
    
    for i in range(6):
        data_map[f"{prefix}_j{i}"] = joint_data[i]
    
    # tcp_labels = ["X", "Y", "Z", "A", "B", "C"]
    # for i, label in enumerate(tcp_labels):
    #     data_map[f"{prefix}_{label}"] = tcp_data[i]
        
    # for i in range(8):
    #     data_map[f"{prefix}_DI_{i}"] = other_data[i]

    for key, current_val in data_map.items():
        if prev_states.get(key) != current_val:
            adapter.update_data(key, current_val)
            prev_states[key] = current_val


if __name__ == "__main__":
    adapter_KUKA = MTConnectAdapter(host='127.0.0.1', port=8200)
    adapter_KUKA.start()
    KUKA_Previous_State = {}

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            print(data)
            xml_kuka = ET.fromstring(data.decode())

            print('Received data:', ET.tostring(xml_kuka, encoding='utf8').decode())

            Joint_Axis = {}
            Torque_Axis = {}

            for child in xml_kuka:
                if child.tag == 'Joint_Axis':
                    for key, value in child.attrib.items():
                        Joint_Axis[key] = float(value)
                elif child.tag == 'Torque_Axis':
                    for key, value in child.attrib.items():
                        Torque_Axis[key] = float(value)

            # print('Joint Axis:', Joint_Axis)

            KUKA_Robot_Joint_Data = Joint_Axis
            KUKA_Robot_TCP_Data = 0
            # KUKA_Robot_Other_Data = kuka_robot_other_data(bridge)
            KUKA_Robot_Other_Data = 0
            update_robot_adapter(adapter_KUKA, "KUKA_", KUKA_Robot_Joint_Data, KUKA_Robot_TCP_Data, KUKA_Robot_Other_Data, KUKA_Previous_State)


    except KeyboardInterrupt:
        print("Exited by the User")
    finally:
        client_socket.close()
        print('Client socket is closed')
        server_socket.close()
        print('Server socket is closed')
        adapter_KUKA.stop()
        print("KUKA RSI Connection Terminated")



