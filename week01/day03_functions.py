def classify_router(router):
    if router['status'] == 'up':
        return 'up'
    elif router['status'] == 'down' and router['site'] == 'HQ':
        return 'critical hq device down'
    elif router['status'] == 'down':
        return 'warning device down'
    elif router['status'] == 'maintenance':
        return 'maintenance'
    else:
        return 'unknown state'

def count_status(devices):
    status_count = {
        'up': 0,
        'down': 0,
        'maintenance': 0,
        'unknown': 0
    }
    
    for router in devices:
        if router['status'] == 'up':
            status_count['up'] += 1
        elif router['status'] == 'down':
            status_count['down'] += 1
        elif router['status'] == 'maintenance':
            status_count['maintenance'] += 1
        else:
            status_count['unknown'] += 1            
    return status_count


devices = [
    {"hostname": "R1", "ip": "10.0.0.1", "site": "HQ", "status": "up"},
    {"hostname": "R2", "ip": "10.0.0.2", "site": "HQ", "status": "down"},
    {"hostname": "R3", "ip": "10.0.0.3", "site": "DR", "status": "up"},
    {"hostname": "R4", "ip": "10.0.0.4", "site": "DR", "status": "maintenance"},
    {"hostname": "R5", "ip": "10.0.0.5", "site": "Branch", "status": "down"}
]

for router in devices:
    classification = classify_router(router)
    print(f"{router['hostname']}: {classification}")

status_summary = count_status(devices)
print("\nStatus Summary:")
for status, count in status_summary.items():
    print(f"{status.capitalize()}: {count}")

