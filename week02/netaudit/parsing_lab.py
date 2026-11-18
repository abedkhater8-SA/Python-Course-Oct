
from ntc_templates.parse import parse_output

raw_output = """
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet1       10.100.100.12   YES manual up                    up
GigabitEthernet2       unassigned      YES unset  administratively down down
GigabitEthernet3       10.20.20.1      YES manual up                    down
"""

interfaces = parse_output(
    platform="cisco_ios",
    command="show ip interface brief",
    data=raw_output
)


for interface in interfaces:

    if (
        interface["status"] != "up"
        or interface["proto"] != "up"
    ):
        print(
            f"{interface['interface']} | "
            f"Status: {interface['status']} | "
            f"Protocol: {interface['proto']}"
        )