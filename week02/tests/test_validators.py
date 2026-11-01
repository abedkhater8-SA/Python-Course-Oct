import pytest

from netaudit.validators import (
    SiteSubnetConfigurationError,
    validate_router_ip
)

def test_valid_router_ip():

    router = {
        "hostname": "R1",
        "ip": "10.10.10.11",
        "site": "HQ"
    }

    site_subnets = {
        "HQ": "10.10.10.0/24"
    }

    result = validate_router_ip(router, site_subnets)

    assert result == "VALID", f"Expected 'VALID', but got {result}"



def test_wrong_subnet():

    router = {
        "hostname": "R2",
        "ip": "10.10.20.12",
        "site": "HQ"
    }

    site_subnets = {
        "HQ": "10.10.10.0/24"
    }

    result = validate_router_ip(router, site_subnets)

    assert result == "WRONG SUBNET"

def test_invalid_site_subnet():

    router = {
        "hostname": "R3",
        "ip": "10.20.20.10",
        "site": "DR"
    }

    site_subnets = {
        "DR": "10.20.20.0/99"
    }

    with pytest.raises(SiteSubnetConfigurationError):
        validate_router_ip(router, site_subnets)

def test_invalid_ip_address():

    router = {
        "hostname": "R4",
        "ip": "10.30.30.300",
        "site": "Branch"
    }

    site_subnets = {
        "Branch": "10.30.30.0/24"
    }

    
    result= validate_router_ip(router, site_subnets)
    assert result == "INVALID IP ADDRESS"

def test_unknown_site():
    
    router = {
        "hostname": "R5",
        "ip": "10.100.100.10",
        "site": "London"
    }

    site_subnets = {
        "HQ": "10.10.10.0/24",
        "DR": "10.20.20.0/24"
    }

    result = validate_router_ip(router, site_subnets)
    assert result == "UNKNOWN SITE"

def test_invalid_ip_address_with_wrong_subnet():
    router = {
        "hostname": "R6",
        "ip": "10.40.40.400",
        "site": "Branch"
    }

    site_subnets = {
        "Branch": "10.10.10.0/200"
    }
    result = validate_router_ip(router, site_subnets)
    assert result == "INVALID IP ADDRESS"


