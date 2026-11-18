from netaudit.interface_parser import parse_router_interfaces


def make_router(hostname, commands, status="success"):
    return {
        "hostname": hostname,
        "host": "10.100.100.12",
        "status": status,
        "data": {
            "commands": commands
        }
    }


VALID_OUTPUT = """
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet1       10.10.10.1      YES manual up                    up
GigabitEthernet2       unassigned      YES unset  administratively down down
GigabitEthernet3       10.30.30.1      YES manual up                    down
"""


def test_valid_output():
    routers = [
        make_router("R1", {"show ip interface brief": VALID_OUTPUT})
    ]

    result = parse_router_interfaces(routers)

    assert result[0]["parse_status"] == "PARSED"
    assert len(result[0]["interfaces"]) == 3
    assert result[0]["interfaces"][2]["proto"] == "down"


def test_missing_command():
    routers = [make_router("R2", {"show version": "Cisco IOS"})]

    result = parse_router_interfaces(routers)

    assert result[0]["parse_status"] == "MISSING_COMMAND"


def test_empty_output():
    routers = [make_router("R3", {"show ip interface brief": "  \n  "})]

    result = parse_router_interfaces(routers)

    assert result[0]["parse_status"] == "EMPTY_OUTPUT"