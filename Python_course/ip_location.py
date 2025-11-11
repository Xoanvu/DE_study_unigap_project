from pymongo import MongoClient
import ip2location
import csv

MONGO_URI = "mongodb://admin:Poiuytrewq@12@127.0.0.1:28018/?authSource=admin"
DB_NAME = "mydb"
SOURCE_COLLECTION = "summary"         # Tên collection chứa IP gốc
TARGET_COLLECTION = "ip_locations"    # Collection lưu kết quả
IP_FIELD = "ip"                       # Tên field chứa địa chỉ IP
BIN_FILE = "IP2LOCATION-LITE-DB3.BIN" # File IP2Location .BIN
CSV_OUTPUT = "ip_locations.csv"       # Tên file CSV xuất ra

def process_ip_locations():
    # 1. Kết nối MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    src_col = db[SOURCE_COLLECTION]
    dest_col = db[TARGET_COLLECTION]

    # 2. Lấy danh sách IP duy nhất
    ips = src_col.distinct(IP_FIELD)
    print(f"Found {len(ips)} unique IPs.")

    # 3. Load IP2Location database
    ip2loc = ip2location.IP2Location(BIN_FILE)

    results = []

    # 4. Xử lý từng IP
    for ip in ips:
        try:
            record = ip2loc.get_all(ip)
            data = {
                "ip": ip,
                "country_short": record.country_short,
                "country_long": record.country_long,
                "region": record.region,
                "city": record.city,
                "latitude": record.latitude,
                "longitude": record.longitude
            }
            results.append(data)
        except Exception as e:
            print(f"Error for IP {ip}: {e}")

    # 5. Ghi vào MongoDB
    if results:
        dest_col.insert_many(results)
        print(f"Inserted {len(results)} records into {TARGET_COLLECTION}")

    # 6. Ghi ra file CSV
    with open(CSV_OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"Saved results to {CSV_OUTPUT}")

process_ip_locations()
