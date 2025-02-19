


# import serial

# ser = serial.Serial('COM5', 9600, timeout=1)
# ser.close() 

# try:
#     ser = serial.Serial('COM5', 9600, timeout=1)
#     print("Serial port opened successfully.")
# except serial.SerialException as e:
#     print(f"Error: {e}")

# read = 0
# ser.write(b'dasdfasdf475 ')

# read = ser.readline().decode('ascii')
# print("Reading: ", read)


# while True:
#     print(ser.name)
#     data = ser.readline().decode('utf-8').strip()
#     print("Reading: ", data)
#     read = ser.readline().decode('ascii')
#     print("Readin2g: ", read)
#     if ser.in_waiting > 0:  
#         print('SS')
#         data = ser.read(ser.in_waiting)  
#         print("Received Data:", data)


import serial

ser = serial.Serial('COM5', 9600, timeout=1)

read = 0

print("Start")
print(ser.name)

ser.write(b'\x0501WSS0106%PW002FFFF\x04')

print("Reading")
read = ser.readline().decode('ascii')
print("Reading: ", read)

ser.close()

