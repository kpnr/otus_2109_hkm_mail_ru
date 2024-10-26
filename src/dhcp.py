"""DCHP games"""

import socket
import random
import enum

# OP field
BOOTREQUEST = 1
BOOTREPLY = 2
DHCP_COOKIE = (99, 130, 83, 99,)


class DHCP_OPTIONS(enum.IntEnum):
    PAD = 0  # Fixed None
    SUBNET_MASK = 1
    ROUTER_OPTION = 3
    DNS_OPTION = 6
    DOMAIN_NAME = 15
    PERFORM_ROUTER_DISCOVERY = 31
    STATIC_ROUTE_OPTION = 33
    VENDOR_INFO = 43
    NBNS_OPTION = 44
    MESSAGE_TYPE = 53  # Len 1
    SERVER_IDENTIFIER = 54
    PARAMETER_REQUEST_LIST = 55 # n-list
    CLIENT_IDENTIFIER = 61 # n-str
    END = 255  # Fixed None


class MESSAGE_TYPE(enum.IntEnum):
    DHCPDISCOVER = 1
    DHCPOFFER = 2
    DHCPREQUEST = 3
    DHCPDECLINE = 4
    DHCPACK = 5
    DHCPNAK = 6
    DHCPRELEASE = 7


def main():
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(1.0)
    sock.bind(('0.0.0.0', 68))
    xid = bytes(random.randrange(0, 256) for _ in range(4))
    msg_discover = bytes((
        BOOTREQUEST,  # OP
        1,  # HTYPE '1' = 10mb ethernet
        6,  # Hardware address length (e.g.  '6' for 10mb ethernet)
        0,  # hops
        *xid,  # Transaction ID
        0, 0,  # secs seconds elapsed since client began address acquisition
        128, 0,  # flags bit0=Broadcast
        0, 0, 0, 0,  # ciaddr Client IP address
        0, 0, 0, 0,  # yiaddr 'your' (client) IP address
        0, 0, 0, 0,  # siaddr IP address of server to use in bootstrap (returned in DHCPOFFER, DHCPACK by server)
        0, 0, 0, 0,  # giaddr Relay agent IP address
        *((0,) * 16),  # chaddr Client hardware address
        *((0,) * 64),  # sname server host name
        *((0,) * 128),  # file Boot file name (DHCPDISCOVER)
        *DHCP_COOKIE,  # Optional parameters field (COOKIE)
        DHCP_OPTIONS.MESSAGE_TYPE, 1, MESSAGE_TYPE.DHCPDISCOVER,
        DHCP_OPTIONS.PARAMETER_REQUEST_LIST, 1, DHCP_OPTIONS.DNS_OPTION,
        DHCP_OPTIONS.END, DHCP_OPTIONS.PAD # EOF
        ))
    m = sock.sendto(msg_discover, ('255.255.255.255', 67))
    m = sock.recvfrom(576)
    print(m)
    return


if '__main__' == __name__:
    main()
