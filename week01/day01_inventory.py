devices = [
    {
        "hostname": "R1",
        "ip": "192.0.2.11",
        "site": "HQ",
        "status": "up"
    },
    {
        "hostname": "R2",
        "ip": "192.0.2.12",
        "site": "HQ",
        "status": "up"
    },
    {
        "hostname": "R3",
        "ip": "192.0.2.13",
        "site": "DR",
        "status": "down"
    }
]

count = 0
count_down = 0

for router in devices:
    print(f"router: {router['hostname']} management ip: {router['ip']} {router['status']}")
    if router['status'] == 'up':
        count += 1
    else:
        count_down += 1

print(f"total devices: {len(devices)}") 
print(f"total devices in up state: {count}")
print(f"total devices in down state: {count_down}")

if len(devices) > 0:
    availability = (count / len(devices)) * 100
else:
    availability = 0

print(f"Availability: {availability:.2f}%")


