import ipaddress


class SiteSubnetConfigurationError(ValueError):
    pass

def validate_router_ip(router, site_subnets):
    if router["site"] not in site_subnets:
        return "UNKNOWN SITE"

    try:
        ip = ipaddress.ip_address(router["ip"])
    except ValueError as error:
        return "INVALID IP ADDRESS"
    
    try:
        subnet = ipaddress.ip_network(
            site_subnets[router["site"]]
        )

    except ValueError as error:
        raise SiteSubnetConfigurationError(
            f"Invalid subnet configuration for site {router['site']}: {error}"
        )

    if ip in subnet:
        return "VALID"
    else:
        return "WRONG SUBNET"


