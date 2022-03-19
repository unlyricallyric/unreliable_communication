import sys
import socket
import argparse

HEADER = 64
PORT = 666
FORMAT = 'utf-8'
SERVER = '10.0.0.120'
ADDR = (SERVER, PORT)
DESCRIPTION = 'httpfs is a simple file server.'
FILE_START = '<START>'
FILE_END = '<END>'

def run_client(commands):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)
        connected = True
        while connected:
            request = commands.encode("utf-8")
            client.sendall(request)
            response = client.recv(2048)
            response = response.decode("utf-8")
            sys.stdout.write("Replied: \n" + response + '\n')
            connected = not connected
    except:
        print("client failed to connect")
    finally:
        client.close()


parser = argparse.ArgumentParser(description=DESCRIPTION, add_help=False)
parser.add_argument('commands', type = str, nargs='*')
parser.add_argument('--host', help='targeting host', default='')
parser.add_argument('--port', help='targeting port', type=int, default=80)
parser.add_argument('--body', help='body of the content', type=str, default='')
parser.add_argument('--client', help='client type, whether httpc or httpfs', default='httpfs')
parser.add_argument('-v', '--v', action='store_true')
parser.add_argument('-p', '--p', default=80)
parser.add_argument('-d', '--d', default='/')

args = parser.parse_args()

if(args.body):
    args.body = FILE_START + str(args.body) + FILE_END

run_client(str(args))