#KUKA 로봇 RSI통신 기반 Adapter

import time
from RobotSensorInterface import RobotSensorInterfaceBridge
from MTConnectAdapter_Base import MTConnectAdapter

bridge = RobotSensorInterfaceBridge() 
bridge.start()
print("Check IP & PORT")

def kuka_robot_joint_data(bridge):
    state = bridge.get_data_sub()
    # 원래 소수점 1자리
    return [f"{state[f'A{i}']:.2f}" for i in range(1, 7)]

def kuka_robot_TCP_data(bridge):
    state = bridge.get_data_sub()
    labels = ["X", "Y", "Z", "A", "B", "C"]
    return [f"{state[label]:.2f}" for label in labels]

# def kuka_robot_other_data(bridge):
#     state = bridge.get_data_sub()
#     return [str(state["ipoc"]), str(state.get("dio", 0))]

def update_robot_adapter(adapter, prefix, joint_data, tcp_data, other_data, prev_states):
    if joint_data is None or tcp_data is None or other_data is None:
        return
    data_map = {}
    
    for i in range(6):
        data_map[f"{prefix}_j{i}"] = joint_data[i]
    
    tcp_labels = ["X", "Y", "Z", "A", "B", "C"]
    for i, label in enumerate(tcp_labels):
        data_map[f"{prefix}_{label}"] = tcp_data[i]
        
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
            state = bridge.get_data_sub() 
            # print(f"[KUKA Robot Data Received] IPOC={state['ipoc']} "
            #         f"X={state['X']:.2f} Y={state['Y']:.2f} Z={state['Z']:.2f}")
            print("KUKA State:", state)
            KUKA_Robot_Joint_Data = kuka_robot_joint_data(bridge)
            KUKA_Robot_TCP_Data = kuka_robot_TCP_data(bridge)
            # KUKA_Robot_Other_Data = kuka_robot_other_data(bridge)
            KUKA_Robot_Other_Data = 0
            update_robot_adapter(adapter_KUKA, "KUKA_", KUKA_Robot_Joint_Data, KUKA_Robot_TCP_Data, KUKA_Robot_Other_Data, KUKA_Previous_State)

    except KeyboardInterrupt:
        print("Exited by the User")
    finally:
        adapter_KUKA.stop()
        bridge.stop()
        print("KUKA RSI Connection Terminated")

