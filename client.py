import socket
import argparse
import sys
from urllib.parse import urlparse

HEADER = 64
PORT = 666
FORMAT = 'utf-8'
SERVER = '10.0.0.120'
ADDR = (SERVER, PORT)
DESCRIPTION = '\nhttpc is a curl-like application but supports HTTP protocol only.\n'
FILE_START = '<START>'
FILE_END = '<END>'

def run_client(commands, args):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)
        connected = True
        while connected:
            request = commands.encode("utf-8")
            client.sendall(request)
            response = client.recv(2048)
            response = response.decode("utf-8")
            if(args.o):
                saveResponse(response, args.o)
            else:
                sys.stdout.write("Replied: \n" + response)
            print("connected!")
            connected = not connected
    except:
        print("client failed to connect")
    finally:
        client.close()
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
parser.add_argument('--host', help='targeting host', default='')
parser.add_argument('--port', help='targeting port', type=int, default=80)
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

run_client(str(args), args)