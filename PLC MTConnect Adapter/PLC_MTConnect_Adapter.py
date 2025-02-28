import sys
import socket
#from urllib.request import localhost

"""
Creating Socket Objects
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



