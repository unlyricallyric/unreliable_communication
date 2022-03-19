import os
import socket
import threading
from urllib.parse import urlparse
from datetime import datetime

PORT = 666
SERVER = ''
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
FILE_START = '<START>'
FILE_END = '<END>'
ERROR_MSG = '301 Moved Permanently'

HOST_KEY = 'host'
PORT_KEY = 'port'
V_KEY = 'v'
H_KEY = 'h'
D_KEY = 'd'
F_KEY = 'f'

USAGE = 'Usage: \n\t httpc command [arguments]\n'
GET_DESCRIPTION = 'exectues a HTTP GET request and prints the response.'
POST_GET_DESCRIPTION = 'executes a HTTPO POST request and prints the response.'
HELP_DESCRIPTION = 'prints this screen.'
COMMANDS = f'The commands are: \n\t get \t {GET_DESCRIPTION} \n\t post \t {POST_GET_DESCRIPTION} \n\t help \t {HELP_DESCRIPTION} \n\n'
HELP_MORE = 'Use \"httpc help [command]\" for more information about a command.'
V_USAGE = '-v \t\t Prints the detail of the response such as protocol, status, and headers.'
H_USAGE = '-h key:value \t Associates headers to HTTP Request with the format\'key:value\'.'
D_USAGE = '-d string \t Associates an inline data to the body HTTP POST request.'
F_USAGE = '-f file \t Associates the content of a file to the body HTTP POST request.'

DESCRIPTION_FILE = '\nhttpfs is a simple file server. \n\n'
USAGE_FILE = 'usage: httpfs [-v] [-p PORT] [-d PATH-TO-DIR] \n\n'
V_USAGE_FILE = '-v \t Prints debugging messages. \n\n'
P_USAGE_FILE = '-p \t Specifies the port number that the server will listen and serve at. \n\t Default is 8080. \n\n'
D_USAGE_FILE = '''
-d \t Specifies the directory that the server will use to read/write requested files. 
\t Default is the current directory when launching the application.
'''

GET = 'Get executes a HTTP GET request for a given URL.'
POST = 'Post executes a HTTP POST request for a given URL with inline data or from file.'
POST_NOTE = 'Either [-d] or [-f] can be used but not both.'
GET_USAGE = f'Usage: httpc get [-v] [-h key:value] URL.'
POST_USAGE = f'usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL.'
DESCRIPTION = '\nhttpc is a curl-like application but supports HTTP protocol only.\n'
LOCKED = '.LOCKED'

HEADER = ('''
HTTP/1.0 {0}
Date: {1}
Server: Apache/1.3.27 (Unix)
MIME-version: 1.0
Content-Type: text/html
Content-Length: {2} \n
{3} ''')

def strToDict(str):
    paramdict = {}
    http_body = ''
    params = str[(str.index(']')+2):len(str)-1]

    if(FILE_START in params):
        http_body = params[params.index(FILE_START)+len(FILE_START):params.index(FILE_END)]
        params = params[0:params.index(FILE_START)] + params[params.index(FILE_END)+len(FILE_END):]

    paramArray = params.split(',')

    for param in paramArray:
        param = param.replace('\'', '')
        param = param.replace(' ', '')
        if(param[0:4] != 'host'):
            pair = param.split('=')
            if((pair[0] == 'd' and 'httpc' in params) or (pair[0] == 'body' and 'httpfs' in params)):
                paramdict[pair[0]] = http_body
            else:
                paramdict[pair[0]] = pair[1]
        else:
            paramdict[HOST_KEY] = param[param.index('=')+1: len(param)]
            
    return paramdict


def commandsToArr(str):
    commands = str[str.index('[') : str.index(']')+1]
    commands = commands.replace('\'', '')
    commands = commands.replace(' ', '')
    commands = commands[1: len(commands)-1]
    arr = commands.split(',')
    return arr

def trimURL(url):
    for c in url:
        if(c == '/'):
            url = url[0:url.index('/')]
            break
    return url

def getResponseBody(response):
    if('{' in response):
        return response[response.index('{'):len(response)]

def getHttpcResponse(commands, params):
    url = ''
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if len(params[HOST_KEY]) != 0:
        url = urlparse(params[HOST_KEY])
    else:
        try:
          url = urlparse(commands[len(commands) - 1])
        except Exception:
            return "Invalid Commands."
    
    url_path = trimURL(url.netloc)
    url_path = socket.gethostbyname(url_path)
    conn.connect((url_path, int(params[PORT_KEY])))

    if(commands[0] == 'get'):
        request = "GET {} HTTP/1.1\r\nHost:{}\r\n\r\n"
        request = request.format(url.path + '?' + url.query, url.netloc)
        conn.send(request.encode(FORMAT))
        response_body = conn.recv(1024)
        response = response_body.decode(FORMAT)

        #check if redirect is needed
        if(ERROR_MSG in response):
            redirect_url = response[response.index('Location:')+len('Location:'):response.index('Cache-Control')].strip()
            url_object = urlparse(redirect_url)
            redirect_request = "GET {} HTTP/1.1\r\nHost:{}\r\n\r\n"
            redirect_request = redirect_request.format(url_object.path + '?' + url_object.query, url_object.netloc)
            conn2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn2.connect((url_object.netloc, 80))
            conn2.send(redirect_request.encode(FORMAT))
            res = conn2.recv(1024).decode(FORMAT)
            response = response + '\n' + res

        if(params[V_KEY] == 'False' and '{' in response):
            return getResponseBody(response)
        return response

    if(commands[0] == 'post'):
        data = params[D_KEY]
        content = params[H_KEY]
        header = ( """
POST /post HTTP/1.1
Host: """ + url_path + """
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.0)
Connection: keep-alive
""" + content + """
""" )
        contentLength = "Content-Length: " + str(len(data)) + "\n\n"
        request = header + contentLength + data
        conn.send(request.encode('utf-8'))
        response = conn.recv(4096)
        return response.decode(FORMAT)


def getHttpfsResponse(commands, params, debugMsg):
    command = commands[0]
    response = ''

    if command == 'help':
        return DESCRIPTION_FILE + USAGE_FILE + V_USAGE_FILE + P_USAGE_FILE + D_USAGE_FILE
    if command == 'get':
        response = getFiles(params, debugMsg)
    if command == 'post':
        response = postFiles(params, debugMsg)
    return str(response)


def getFiles(params, debugMsg):
    path = params['d']
    
    if isLocked(path):
        error_msg = 'File already in use!'
        return HEADER.format('404 Not Found', datetime.now(), len(error_msg.encode('utf-8')), error_msg)

    isFile = os.path.isfile(path)
    isDir = os.path.isdir(path)

    error_msg = 'invalid path or path does not exist'

    if hasWritePermission(path):
        if(isDir):
            return os.listdir(path)
        elif(isFile):
            try:
                locked_path = path + LOCKED
                os.rename(path, locked_path)
                f = open(locked_path, "r")
                content = f.read()
                f.close()
                if(params['v'] == 'True'):
                    content += '\n' + debugMsg
                return HEADER.format('200 OK', datetime.now(), len(content.encode('utf-8')), content)
            except OSError:
                print(error_msg)
            finally:
                os.rename(locked_path, path)

        else:
            return HEADER.format('404 Not Found', datetime.now(), len(error_msg.encode('utf-8')), error_msg)
    error_msg = 'You do not have permission to the requested directory'
    return HEADER.format('404 Not Found', datetime.now(), len(error_msg.encode('utf-8')), error_msg)



def postFiles(params, debugMsg):
    path = params['d']
    response = ''
    error_msg = ''
    f = None
    if isLocked(path):
        error_msg = 'File already in use!'
        return HEADER.format('404 Not Found', datetime.now(), len(error_msg.encode('utf-8')), error_msg)

    if hasWritePermission(params['d']):

        try:
            locked_path = path + LOCKED
            if not isFile(path):
                f = open(path, 'w')
                f.close()
            os.rename(path, locked_path)
            f = open(locked_path, 'w')
            f.write(params['body'])
            f.close()
            response = 'successfully processed request!'
            if(params['v'] == 'True'):
                response += '\n' + debugMsg
            return HEADER.format('200 OK', datetime.now(), len(response.encode('utf-8')), response)
        except OSError:
            print(error_msg)
        finally:
            os.rename(locked_path, path)
    response = 'you do not have write permission to the file'
    return HEADER.format('403 Forbidden', datetime.now(), len(response.encode('utf-8')), response)


def isLocked(file):
    return os.path.exists(file + LOCKED)


def hasWritePermission(path):
    cwd = os.path.abspath(os.getcwd())
    request_path = os.path.abspath(path)

    if cwd in request_path:
        return True
    
    return False

def isDir(path):
    return os.path.isdir(path)


def isFile(path):
    return os.path.isfile(path)


def analyze_args(commands, params, debugMsg):

    client_type = params['client']
    response = ''

    if client_type == 'httpc':
        
        if(commands[0] == 'help'):
            if (len(commands) > 1):
                if(commands[1] == 'get'):
                    return f'{GET_USAGE} \n\n {GET} \n\n {V_USAGE} \n {H_USAGE}'

                if(commands[1] == 'post'):
                    return f'{POST_USAGE} \n\n {POST} \n\n {V_USAGE} \n {H_USAGE} \n {D_USAGE} \n {F_USAGE} \n\n {POST_NOTE}'
            else:
                return DESCRIPTION + USAGE + COMMANDS + HELP_MORE
        response = getHttpcResponse(commands, params)

    if client_type == 'httpfs':
        response = getHttpfsResponse(commands, params, debugMsg)

    return response
    

def handle_client(conn, addr):

    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        while True:
            data = conn.recv(1024)
            if data:
                params = strToDict(data.decode(FORMAT))
                debugMsg = '\n ##### DEBUGGING MESSAGE ##### \n This is the params received: \n' + str(params)
                commands = commandsToArr(data.decode(FORMAT))
                debugMsg = debugMsg + '\n this is the commands received: \n' + str(commands) + '\n'
                msg = analyze_args(commands, params, debugMsg)
                conn.sendall(msg.encode(FORMAT))
    finally:
        conn.close()

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind(ADDR)
        server.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")

        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    finally:
        server.close()

print("[STARTING] server is starting...")
start()
