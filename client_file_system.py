import sys
import socket
import argparse
import ipaddress

from packet import Packet


FORMAT = 'utf-8'
DESCRIPTION = 'httpfs is a simple file server.'
FILE_START = '<START>'
FILE_END = '<END>'

def run_client(commands, args):
    server_addr = args.serverhost
    server_port = args.serverport
    router_addr = args.routerhost
    router_port = args.routerport

    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    timeout = 5

    try:
        p = Packet(packet_type=0,
                   seq_num=1,
                   peer_ip_addr=peer_ip,
                   peer_port=server_port,
                   payload=commands.encode("utf-8"))
        conn.sendto(p.to_bytes(), (router_addr, router_port))

        conn.settimeout(timeout)
        print('Waiting for a response')
        response, sender = conn.recvfrom(1024)
        p = Packet.from_bytes(response)
        print('Router: ', sender)
        print('Payload: ' + p.payload.decode("utf-8"))

    except socket.timeout:
        print('No response after {}s'.format(timeout))
    finally:
        conn.close()


parser = argparse.ArgumentParser(description=DESCRIPTION, add_help=False)
parser.add_argument('commands', type = str, nargs='*')
parser.add_argument('--serverhost', help='targeting host', default='localhost')
parser.add_argument('--serverport', help='targeting port', type=int, default=8007)
parser.add_argument("--routerhost", help="router host", default="localhost")
parser.add_argument("--routerport", help="router port", type=int, default=3000)
parser.add_argument('--body', help='body of the content', type=str, default='')
parser.add_argument('--client', help='client type, whether httpc or httpfs', default='httpfs')
parser.add_argument('-v', '--v', action='store_true')
parser.add_argument('-p', '--p', default=80)
parser.add_argument('-d', '--d', default='/')

args = parser.parse_args()

if(args.body):
    args.body = FILE_START + str(args.body) + FILE_END

run_client(str(args), args)