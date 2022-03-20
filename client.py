import socket
import argparse
import ipaddress
import sys

from urllib.parse import urlparse
from packet import Packet

FORMAT = 'utf-8'
DESCRIPTION = '\nhttpc is a curl-like application but supports HTTP protocol only.\n'
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
#List to String
def listToString(s):
    str1 = ""
    for ele in s:
        str1 += ele
    return str1

def getHttpBody(file):
    f = open(file, 'r')
    return f.read()

def saveResponse(response, dir):
    f = open(dir, 'a')
    if('{' in response):
        response = response[response.index('{'):len(response)]
    f.write(response)
    f.close()

#Extract operation flags from the command line arguments
arg_func = ''
arg_temp = []
if(len(sys.argv) >= 2):
  arg_temp = sys.argv[2:]
  arg_func = sys.argv[1]

#Parsing Rules
parser = argparse.ArgumentParser(description=DESCRIPTION, add_help=False)
parser.add_argument('commands', type = str, nargs='*')
parser.add_argument('--serverhost', help='targeting host', default='localhost')
parser.add_argument('--serverport', help='targeting port', type=int, default=8007)
parser.add_argument("--routerhost", help="router host", default="localhost")
parser.add_argument("--routerport", help="router port", type=int, default=3000)
parser.add_argument('--client', help='client type, whether httpc or httpf', default='httpc')
parser.add_argument('-v', '--v', action='store_true', help='Prints the detail of the response such as protocol, status, and headers.')
parser.add_argument('-h', '--h', help='Associates headers to HTTP Request with the format \'key:value\'.')
parser.add_argument('-d', '--d', help='Associates an inline data to the body HTTP POST request')
parser.add_argument('-f', '--f', help='Associates the content of a file to the body HTTP POST request')
parser.add_argument('-o', '--o', help='Save http response body into the indicated local file')

#Enforce the parsing rule on the argument string whose function name is extracted.
args = parser.parse_args(arg_temp)


#Locate the URL at the last position
url = arg_temp[len(arg_temp) - 1] if len(arg_temp) != 0 else ''

# If no url included then we dont push into the command list
if url != '':
    args.commands.append(url)

#Append the function name into the first element of the command list.
if (len(args.commands) == 0):
    args.commands.append(arg_func)
else:
    args.commands[0] = arg_func

if(args.f):
    args.d = FILE_START + getHttpBody(args.f) + FILE_END
else:
    args.d = FILE_START + str(args.d) + FILE_END

#print(args)
run_client(str(args), args)