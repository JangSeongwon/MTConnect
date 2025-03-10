import socket
import threading
import time

class MTConnectAdapter:
    def __init__(self, host='127.0.0.1', port=7878):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connections = []
        self.running = False
        self.current_data = {}

    def start(self):
        self.running = True
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        print(f"[Adapter] Listening on {self.host}:{self.port}")

        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while self.running:
            conn, addr = self.sock.accept()
            self.connections.append(conn)
            print(f"[Adapter] Connected by {addr}")
            threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()

    def handle_client(self, conn):
        while self.running:
            try:
                data_str = self.format_data_for_mtconnect()
                print("ROS Data Update : ", data_str)
                conn.sendall(data_str.encode('utf-8'))
                time.sleep(0.5)  # 0.5초 간격 예시
            except (BrokenPipeError, ConnectionResetError):
                break

    def format_data_for_mtconnect(self):
        timestamp = str(int(time.time()))  # epoch time
        data_items = []

        for key, value in self.current_data.items():
            data_items.append(f"{key}|{value}")

        return timestamp + '|' + '|'.join(data_items) + '\n'

    def update_data(self, key, value):
        # ROS 데이터 저장
        self.current_data[key] = value

    def stop(self):
        self.running = False
        for conn in self.connections:
            conn.close()
        self.sock.close()
