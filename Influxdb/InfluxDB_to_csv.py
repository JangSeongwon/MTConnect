import csv
from influxdb import InfluxDBClient

# InfluxDB 설정
INFLUXDB_HOST = "localhost"
INFLUXDB_PORT = 8086
INFLUXDB_DB = "robot"
INFLUXDB_MEASUREMENT = "mtconnect"
OUTPUT_CSV_FILE = "/home/sms/InfluxDB/influxdb_data.csv"

def export_influxdb_to_csv():
    client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
    client.switch_database(INFLUXDB_DB)

    # 로봇 + switch
    query = f"""
    SELECT time,
        "A0912_j0", "A0912_j1", "A0912_j2", "A0912_j3", "A0912_j4", "A0912_j5",
        "A0912_X", "A0912_Y", "A0912_Z", "A0912_Rx", "A0912_Ry", "A0912_Rz", "A0912_solutionspace",
        "M1013_j0", "M1013_j1", "M1013_j2", "M1013_j3", "M1013_j4", "M1013_j5",
        "M1013_X", "M1013_Y", "M1013_Z", "M1013_Rx", "M1013_Ry", "M1013_Rz", "M1013_solutionspace",
        "Switch"
    FROM {INFLUXDB_MEASUREMENT}
    ORDER BY time DESC
    """

    result = client.query(query)
    points = list(result.get_points())

    if not points:
        print("Noi data")
        return

    # 헤더 설정
    headers = [
        "time",
        "A0912_j0", "A0912_j1", "A0912_j2", "A0912_j3", "A0912_j4", "A0912_j5",
        "A0912_X", "A0912_Y", "A0912_Z", "A0912_Rx", "A0912_Ry", "A0912_Rz", "A0912_solutionspace",
        "M1013_j0", "M1013_j1", "M1013_j2", "M1013_j3", "M1013_j4", "M1013_j5",
        "M1013_X", "M1013_Y", "M1013_Z", "M1013_Rx", "M1013_Ry", "M1013_Rz", "M1013_solutionspace",
        "Switch"
    ]

    with open(OUTPUT_CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        for point in points:
            row = [point.get(h, "N/A") for h in headers]
            writer.writerow(row)

    print(f"InfluxDB saved")
    client.close()

if __name__ == "__main__":
    export_influxdb_to_csv()