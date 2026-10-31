import ipaddress

site_subnets = {
    "HQ": "10.10.10.0/24",
    "DR": "10.20.20.0/24",
    "Branch": "10.30.30.0/24"
}

devices = [
    {"hostname": "R1", "ip": "10.10.10.11", "site": "HQ"},
    {"hostname": "R2", "ip": "10.10.20.12", "site": "HQ"},
    {"hostname": "R3", "ip": "10.20.20.10", "site": "DR"},
    {"hostname": "R4", "ip": "10.30.30.5", "site": "Branch"},
    {"hostname": "R5", "ip": "10.20.20.999", "site": "DR"},
    {"hostname": "R6", "ip": "10.40.40.10", "site": "DC2"}
]


def validate_router_ip(router, site_subnets):
    
    if router["site"] not in site_subnets:
        return  "UNKNOWN_SITE"
    
    try:
        ip = ipaddress.ip_address(router["ip"])
    except ValueError:
        return "INVALID_IP"
    
    subnet = ipaddress.ip_network(site_subnets[router["site"]])
    if ip in subnet:
        return "VALID_IP"
    else:
        return "WRONG_SUBNET"


for router in devices:
    result = validate_router_ip(router, site_subnets)
    print(result)




    