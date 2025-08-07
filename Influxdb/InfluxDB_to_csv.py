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
    # query = f"""
    # SELECT time,
    #     "A0912_j0", "A0912_j1", "A0912_j2", "A0912_j3", "A0912_j4", "A0912_j5",
    #     "A0912_X", "A0912_Y", "A0912_Z", "A0912_Rx", "A0912_Ry", "A0912_Rz", "A0912_solutionspace",
    #     "M1509_j0", "M1509_j1", "M1509_j2", "M1509_j3", "M1509_j4", "M1509_j5",
    #     "M1509_X", "M1509_Y", "M1509_Z", "M1509_Rx", "M1509_Ry", "M1509_Rz", "M1509_solutionspace",
    #     "Switch"
    # FROM {INFLUXDB_MEASUREMENT}
    # ORDER BY time DESC
    # """
    query = f"""
    SELECT time,
        "M1509_j0", "M1509_j1", "M1509_j2", "M1509_j3", "M1509_j4", "M1509_j5",
        "M1509_X", "M1509_Y", "M1509_Z", "M1509_Rx", "M1509_Ry", "M1509_Rz", "M1509_solutionspace",
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
    # headers = [
    #     "time",
    #     "A0912_j0", "A0912_j1", "A0912_j2", "A0912_j3", "A0912_j4", "A0912_j5",
    #     "A0912_X", "A0912_Y", "A0912_Z", "A0912_Rx", "A0912_Ry", "A0912_Rz", "A0912_solutionspace",
    #     "M1509_j0", "M1509_j1", "M1509_j2", "M1509_j3", "M1509_j4", "M1509_j5",
    #     "M1509_X", "M1509_Y", "M1509_Z", "M1509_Rx", "M1509_Ry", "M1509_Rz", "M1509_solutionspace",
    #     "Switch"
    # ]
    headers = [
        "time",
        "M1509_j0", "M1509_j1", "M1509_j2", "M1509_j3", "M1509_j4", "M1509_j5",
        "M1509_X", "M1509_Y", "M1509_Z", "M1509_Rx", "M1509_Ry", "M1509_Rz", "M1509_solutionspace",
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