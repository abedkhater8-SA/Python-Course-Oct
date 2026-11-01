devices = [
    {"hostname": "R1", "ip": "10.0.0.1", "site": "HQ", "status": "up"},
    {"hostname": "R2", "ip": "10.0.0.2", "site": "HQ", "status": "down"},
    {"hostname": "R3", "ip": "10.0.0.3", "site": "DR", "status": "up"},
    {"hostname": "R4", "ip": "10.0.0.4", "site": "DR", "status": "maintenance"},
    {"hostname": "R5", "ip": "10.0.0.5", "site": "Branch", "status": "down"}
]

down = 0
maintenance = 0
up = 0
hq_routers = []

for router in devices:
    if router['site'] == 'HQ':
        hq_routers.append(router)
    if router['status'] == 'up':
        up += 1
    elif router['status'] == 'down' and router['site'] == 'HQ':
        down += 1
        print(f"CRITICAL: HQ router {router['hostname']} is down")
    elif router['status'] == 'down' and router['site'] == 'DR':
        down += 1
        print(f"WARNING: DR router {router['hostname']} is down")
    elif router['status'] == 'maintenance':
        maintenance += 1
    else:
        print(f"INFO: Router {router['hostname']} is in an unknown state")

print("====HQ Routers====")
for router in hq_routers:
    print(f"Router: {router['hostname']} IP: {router['ip']} Status: {router['status']}")
    
print("====Summary===")
print(f"Total routers: {len(devices)}")
print(f"Total routers in up state: {up}")
print(f"Total routers in down state: {down}")
print(f"Total routers in maintenance state: {maintenance}")


    