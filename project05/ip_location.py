from pymongo import MongoClient
from datetime import datetime
import IP2Location
import csv

start_time = datetime.now()
print("Start time:", start_time)

batch_size = 100000

# def process_ip_locations():
# 1. Kết nối MongoDB
client = MongoClient("mongodb://admin:Poiuytrewq%4012@35.240.135.255:28018/?authSource=admin")
db = client["mydb"]
collection = db["summary"]
# print("Các index hiện có trong collection 'summary':")
# for index in collection.list_indexes():
#     print(index) # Check connection database

# 2. Lấy danh sách IP duy nhất từ collection chính
ip_unique = collection.aggregate([
    {"$group": {"_id": "$ip"}}
    # ,{"$count": "unique_ip_count"}
], allowDiskUse=True)

# for doc in ip_unique:
#     print("Số lượng IP unique:", doc["unique_ip_count"])
# Số lượng IP unique: 3239628

unique_ips = [doc["_id"] for doc in ip_unique]

# 3. Khởi tạo IP2Location (dùng file BIN hoặc API)
ip2loc = IP2Location.IP2Location("IP2LOCATION-LITE-DB3.BIN")

results = []
total_count = 0

csv_file = open("ip_locations.csv", "w", newline="", encoding="utf-8")
csv_writer = None

for ip in unique_ips:
    try:
        rec = ip2loc.get_all(ip)
        result = {
            "ip": ip,
            "country": rec.country_short,
            "region": rec.region,
            "city": rec.city,
            "latitude": rec.latitude,
            "longitude": rec.longitude
        }
        results.append(result)
    except Exception as e:
        print(f"Lỗi xử lý IP {ip}: {e}")

    if len(results) >= batch_size:
        # 4a. Ghi kết quả vào MongoDB (collection mới)
        db["ip_locations"].insert_many(results)

        # Lưu CSV
        if csv_writer is None and results:
            csv_writer = csv.DictWriter(csv_file, fieldnames=results[0].keys())
            csv_writer.writeheader()
        if csv_writer:
            csv_writer.writerows(results)

        total_count += len(results)
        results = []

        # In log
        end_time = datetime.now()
        print(f"Đã lưu {total_count} IP, thời gian: {end_time}")

# Lưu phần còn lại
if results:
    db["ip_locations"].insert_many(results)
    if csv_writer:
        csv_writer.writerows(results)
    total_count += len(results)
    end_time = datetime.now() - start_time
    print(f"Đã lưu {total_count} IP, thời gian: {end_time}")

csv_file.close()

print("Hoàn tất xử lý IP locations.")

# process_ip_locations()

end_time = datetime.now()
print("End time:", end_time)