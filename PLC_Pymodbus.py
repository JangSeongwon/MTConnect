# Python 3.11.9 버전 작성
# PLC PC 기본 통신 코드
import logging
from pymodbus.client.sync import ModbusSerialClient
logging.basicConfig(level=logging.DEBUG)

# Modbus RTU 설정
client = ModbusSerialClient(
    method='rtu',
    port='COM5',  # Windows: 'COM5', Linux: '/dev/ttyUSB0'
    baudrate=38400,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=5,
    strict=False
)

client.connect()
print("Modbus connected")

# result = client.read_coils(1)
# print(result)

if client.connect():
    write_result = client.write_register(address=1, value=33, slave=1)
    print('Write', write_result)

    # PLC에서 Holding Register 0번 주소 (D100) 읽기
    # count=1 은 16비트로 1개 WORD
    result = client.read_holding_registers(address=1000, count=1, slave=1)
    print('Read', result)

    if result.isError():
        print("읽기 실패:", result)
    else:
        print("PLC 데이터:", result.registers)

    client.close()
else:
    print("Modbus 연결 실패!")
