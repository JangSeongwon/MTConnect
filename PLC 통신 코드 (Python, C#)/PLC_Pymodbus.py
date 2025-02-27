# Python 3.11.9 버전 작성
# PLC PC 기본 통신 코드 
import logging
from pymodbus.client import ModbusSerialClient
# logging.basicConfig(level=logging.DEBUG)

# Modbus RTU 설정
client = ModbusSerialClient(
    port='COM5',  # Windows: 'COM5', Linux: '/dev/ttyUSB0'
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

    print('Receiving Start')
    # PLC에서 Holding Register 0번 주소 (D100) 읽기
    # count=1 은 16bit로 1개 WORD
    result = client.read_holding_registers( address=100, count=1, slave=1)
    print('Read', result)

    if result.isError():
        print("Reading Fail:", result)
    else:
        print("PLC Data read:", result.registers)

    client.close()
else:
    print("Modbus Connect Fail!")

