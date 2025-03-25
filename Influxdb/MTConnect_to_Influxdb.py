
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

# InfluxDB 설정
INFLUXDB_URL = "http://localhost:8086/write?db=robot"
INFLUXDB_TOKEN = "your_token"

# MTConnect Agent 설정
MTCONNECT_URL = "http://localhost:5001/current"

headers = {
    "Authorization": f"Token {INFLUXDB_TOKEN}",
    "Content-Type": "application/x-www-form-urlencoded"
}

# 저장할 데이터 리스트 (robot_mode_id 제외)
VALID_DATA_ITEMS = [
    "A0912_j0", "A0912_j1", "A0912_j2", "A0912_j3", "A0912_j4", "A0912_j5",
    "A0912_X", "A0912_Y", "A0912_Z",
    "A0912_Rx", "A0912_Ry", "A0912_Rz",
    "A0912_solutionspace", "A0912_mode_id"
    "M1013_j0", "M1013_j1", "M1013_j2", "M1013_j3", "M1013_j4", "M1013_j5",
    "M1013_X", "M1013_Y", "M1013_Z",
    "M1013_Rx", "M1013_Ry", "M1013_Rz",
    "M1013_solutionspace", "M1013_mode_id",
    "Switch"
]

def get_mtconnect_data():
    """MTConnect Agent에서 데이터 가져오기"""
    response = requests.get(MTCONNECT_URL)
    
    if response.status_code == 200:
        return response.text # XML 데이터 반환
    else:
        print(f"❌ MTConnect 데이터 수신 실패: {response.status_code}")
        return None

def parse_mtconnect_data(xml_data):
    """MTConnect XML 데이터를 파싱하여 InfluxDB용 데이터 포맷으로 변환"""
    root = ET.fromstring(xml_data)
    ns = {'mt': 'urn:mtconnect.org:MTConnectStreams:2.3'}
    data_list = []

    for device in root.findall(".//mt:DeviceStream", ns):
        uuid = device.get("uuid", "UNKNOWN")
        device_name = device.get("name")
        print(device_name)

        for component in device.findall(".//mt:ComponentStream", ns):
            for event in component.findall(".//mt:Events/*", ns):
                data_id = event.get("dataItemId")
                if data_id not in VALID_DATA_ITEMS:
                    continue

                value = event.text
                if value == "UNAVAILABLE":
                    continue

                timestamp_str = event.get("timestamp")
                try:
                    # 마이크로초(µs)에서 나노초(ns)로 변환
                    timestamp = int(datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp() * 1e6) * 1000
                except ValueError:
                    print(f"⛔ Timestamp format error: {timestamp_str}")
                    continue

                if data_id == "Solution_space":
                    value = f"{int(float(value))}i" # 정수 값에 `i` 추가
                else:
                    value = float(value) # 부동소수점 값 변환

                line_protocol = f"mtconnect,uuid={uuid},device={device_name} {data_id}={value} {timestamp}"
                data_list.append(line_protocol)

            for sample in component.findall(".//mt:Samples/*", ns):
                data_id = sample.get("dataItemId")
                if data_id not in VALID_DATA_ITEMS:
                    continue

                value = sample.text
                if value == "UNAVAILABLE":
                    continue

                timestamp_str = sample.get("timestamp")
                try:
                    # 마이크로초(µs)에서 나노초(ns)로 변환
                    timestamp = int(datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp() * 1e6) * 1000
                    print(timestamp_str)
                except ValueError:
                    print(f"⛔ Timestamp format error: {timestamp_str}")
                    continue

                if data_id == "Solution_space":
                    value = f"{int(float(value))}i"
                else:
                    value = float(value)

                line_protocol = f"mtconnect,uuid={uuid},device={device_name} {data_id}={value} {timestamp}"
                data_list.append(line_protocol)

    return data_list

def write_to_influxdb(data_list):
    """InfluxDB에 모든 데이터 저장"""
    if not data_list:
        return

    data = "\n".join(data_list)
    response = requests.post(INFLUXDB_URL, headers=headers, data=data)

    if response.status_code == 204:
        print(f"✅ InfluxDB에 데이터 저장 완료: {len(data_list)}개 데이터")
    else:
        print(f"❌ InfluxDB 저장 실패: {response.status_code} {response.text}")

if __name__ == '__main__':
    while True:
        xml_data = get_mtconnect_data()
        if xml_data:
            data_list = parse_mtconnect_data(xml_data)
            write_to_influxdb(data_list)