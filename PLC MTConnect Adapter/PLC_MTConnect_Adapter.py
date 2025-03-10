# PLC PC 기본 통신 코드 
import sys, time, datetime, threading
import socket
import logging
from pymodbus.client import ModbusSerialClient

"""
Modbus Connection
"""

client = ModbusSerialClient(
    port='COM6',  # Windows: 'COM6', Linux: '/dev/ttyUSB0'
    baudrate=19200,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout= 1
)

client.connect()
# result1 = client.read_coils(1)
# print(result1)

if client.connect(): 
    print("Modbus connected")
    # write_result = client.write_register(address=105, value=33, slave=1)
    # print('Write', write_result)
else:
    print("Modbus Connect Fail!")


client_counter = 0
client_list = []
first_run_flag = 1
lock = threading.Lock()
event = threading.Event()
event.set()

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
        
def plc_adapter():

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




