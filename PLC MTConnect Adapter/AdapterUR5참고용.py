import threading, time, socket, sys, datetime, random
from urllib.request import localhost

client_counter = 0
client_list = []
first_run_flag = 1
lock = threading.Lock()
event = threading.Event()
event.set()

# Initialising 6 global attributes for UR5 serial comm macros
jointangle0 = jointangle1 = jointangle2 = jointangle3 = jointangle4 = jointangle5 = 'Nil'

"""
Creating Socket Objects
본 프로그램이 돌아가는 PC의 IP address, Port를 입력

"""
HOST = 'localhost' #hostname
PORT = 7880 #Portnumber

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


"""Function to Clear Out Threads List Once All Threads are Empty"""

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


"""Function that parses attributes from the UR5"""

def fetch_from_UR5(): #defines the funtion to retirve data from the UR5 by python    
    global jointangle0, jointangle1, jointangle2, jointangle3, jointangle4, jointangle5, combined_output, grippervariable, jointangle0_prev,jointangle1_prev,jointangle2_prev,jointangle5_prev,jointangle3_prev,jointangle4_prev
    #Global, modify the variable outside of the current scope. It is used to create a global variable and make changes to the variable in a local context with the variables
    while True:
        #print ("while loop....")
        # 로봇으로부터 데이터 받는 부분 (우리 방식으로 custom)
        
        # response = requests.get("http://192.168.1.7/api/devicxecData/UR5") 
        # data = response.json()
        #data = ""
        
        #in order to record change of angle in six joints they are set to "NONE" for first try 
        jointangle0_prev = "None"
        jointangle1_prev = "None"
        jointangle2_prev = "None"
        jointangle5_prev = "None"
        jointangle3_prev = "None"
        jointangle4_prev = "None"    
        grippervariable = "OPEN"
        out_initial = '|j0|' + 'Nil' + '|j1|' + 'Nil' + '|j2|' + 'Nil' + '|j3|' + 'Nil' + '|j4|' + 'Nil' + '|j5|' + 'Nil' +'|gripperstate1|' + 'Nil'

        # combined_output = '\r\n' + datetime.datetime.utcnow().isoformat() + 'Z' + out_initial 
        #Shows the angle and the time at which it was taken
        # time.sleep(2) 
        updated = False
        out = ''
        try:
            #So that the new angles don't have value
            jointangle0 = ""
            jointangle1 = ""
            jointangle2 = ""
            jointangle3 = ""
            jointangle4 = ""
            jointangle5 = ""
            try:
                # jointangle0 = data["data"]["x"]["value"] #values for the first joint # 원본
                jointangle0 = random.random()  #임의의 값
            except:                
                jointangle0 = 'Nil'
            if jointangle0 != jointangle0_prev: #if new angle is different than past then show 
                updated = True
                out += "|j0|" + str(jointangle0)
                jointangle0_prev = jointangle0
                
            try:
                #jointangle1 = data["data"]["y"]["value"] #values for the second joint  # 원본
                jointangle1 = random.random() #values for the first joint #임의의 값
            except:
                jointangle1 = 'Nil'
            if jointangle1 != jointangle1_prev: #if new angle is different than past then show 
                updated = True
                out += "|j1|" + str(jointangle1)
                jointangle1_prev = jointangle1
            try:
                # jointangle2 = data["data"]["z"]["value"] #values for the third joint
                jointangle2 = random.random() #values for the first joint #임의의 값
            except:
                jointangle2 = 'Nil'
            if jointangle2 != jointangle2_prev: #if new angle is different than past then show 
                updated = True
                out += "|j2|" + str(jointangle2)
                jointangle2_prev = jointangle2
            try:
                #jointangle3 = data["data"]["rx"]["value"] #values for the forth joint
                jointangle3 = random.random() #임의의 값
            except:
                jointangle3 = 'Nil'
            if jointangle3 != jointangle3_prev: #if new angle is different than past then show 
                updated = True
                out += "|j3|" + str(jointangle3)
                jointangle3_prev = jointangle3

            try:
                # jointangle4 = data["data"]["ry"]["value"] #values for the fifth joint
                jointangle4 = random.random() #임의의 값
            except:
                jointangle4 = 'Nil'
            if jointangle4 != jointangle4_prev: #if new angle is different than past then show 
                updated = True
                out += "|j4|" + str(jointangle4)
                jointangle4_prev = jointangle4
            try:
                # jointangle5 = data["data"]["rz"]["value"] #values for the sixth joint
                jointangle5 = random.random() #임의의 값
            except: 
                jointangle5 = 'Nil'
            if jointangle5 != jointangle5_prev: #if new angle is different than past then show 
                updated = True
                out += "|j5|" + str(jointangle5)
                jointangle5_prev = jointangle5

            if grippervariable == 'OPEN': 
                if jointangle0 >=-0.23 and jointangle0 <= -0.18: #if Base is in between -0.23 and -0.18 then gripper is closed
                    grippervariable = "CLOSED"
            elif grippervariable == 'CLOSED':
                if jointangle0 >= -3.43 and jointangle0 <= -3.38: #if Base is in between -3.43 and -3.38 then gripper is open
                    grippervariable = 'OPEN'
            out += "|gripperstate|" + grippervariable

            # for each variable you're reading, obtain the value (as a string) and set it equal to the "current" variable declared above.
            # next, compare it to the previous value.
            # if they are equal, do nothing.
            # if they are different, add |VAR.NAME|VAR.VALUE to the out string.
            # ex: out += "|xPos|" + XPositionCurrent
        except Exception as ex:
                print("Failed fetching values from machine " + ex)
                time.sleep(2)           
            
    #end of input
    #### Data with 6 joints

        # end section -----------------------------       
        
        time.sleep(0.1)
        if not updated:
            pass
        combined_output = '\r\n' + datetime.datetime.now().isoformat() + 'Z' + out     
                
        if not event.is_set():
            print("Closing fetch_from_UR5 thread..")
            return

        

#Main Thread Class For Clients
class NewClientThread(threading.Thread):
    # init method called on thread object creation,
    def __init__(self, conn, string_address):
        threading.Thread.__init__(self)
        self.connection_object = conn
        self.client_ip = string_address

    # run method called on .start() execution
    def run(self):
        global client_counter, combined_output
        global lock
        while True:
            try:
                #print("Sending data to Client {} in {}".format(self.client_ip, self.getName()))
                out = combined_output
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
t2 = threading.Thread(target=fetch_from_UR5)
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
        print("\nExiting Program in event.is_set() while loop")
        event.clear()
        break


# if not event.is_set():
#     print("\nExiting Program  in event.is_set() if")
#     sys.exit()
