# Python 3.11.9 버전 작성
# PLC PC 기본 통신 코

from pymodbus.client import ModbusSerialClient

# Modbus RTU 설정
client = ModbusSerialClient(
    port='COM3',  # Windows: 'COM3', Linux: '/dev/ttyUSB0'
    baudrate=115200,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1
)

if client.connect():
    print("Modbus 연결 성공!")

    # PLC에서 Holding Register 0번 주소 (D100) 읽기
    result = client.read_holding_registers(address=0, count=1)

    if result.isError():
        print("읽기 실패:", result)
    else:
        print("PLC 데이터:", result.registers)

    client.close()
else:
    print("Modbus 연결 실패!")


