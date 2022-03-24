import sys
import socket
import argparse
import ipaddress

from packet import Packet, PACKAGE_TYPE


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
    completed = False
    while not completed:
        requesting = True
        try:
            p = Packet(packet_type=0,
                    seq_num=1,
                    peer_ip_addr=peer_ip,
                    peer_port=server_port,
                    payload='')
            conn.sendto(p.to_bytes(), (router_addr, router_port))

            conn.settimeout(timeout)
            while requesting:
                print('Waiting for a response')
                response, sender = conn.recvfrom(1024)
                if not response:
                    print('no data found')
                    break
                response_p = Packet.from_bytes(response)
                print('Package Type: ' + PACKAGE_TYPE[response_p.packet_type])
                if (PACKAGE_TYPE[response_p.packet_type] == 'SYN_ACK'):
                    new_p = Packet(packet_type=2,
                        seq_num=1,
                        peer_ip_addr=peer_ip,
                        peer_port=server_port,
                        payload=commands.encode("utf-8"))
                    conn.sendto(new_p.to_bytes(), (router_addr, router_port))
                elif (PACKAGE_TYPE[response_p.packet_type] == 'ACK'):
                    print('Payload: ' + response_p.payload.decode("utf-8"))
                    completed = True
                    requesting = False
                else:
                    requesting = False

        except socket.timeout:
            print('################ \n\n No response after {}s\nResending Request \n\n ################'.format(timeout))
            print('Resending Request')


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