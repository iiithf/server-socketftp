#!/usr/bin/env python3
from urllib.parse import urlparse
import socket
import sys


# Main
input_url = '127.0.0.1:2001'
if len(sys.argv)>1:
  input_url = sys.argv[1]
if 'ftp://' not in input_url:
  input_url = 'ftp://'+input_url
url = urlparse(input_url)
host = url.hostname
port = 21 if url.port is None else url.port
path = '/' if len(url.path)==0 else url.path
s_ctrl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addr_ctrl = (host, port)
print('Connecting to control', addr_ctrl)
s_ctrl.connect(addr_ctrl)
print('Sending PASV command ...')
s_ctrl.sendall(b'PASV\r\n')
recv_data = s_ctrl.recv(1024)
line_end = recv_data.index(b'\r\n')
line = recv_data[0:line_end].decode('ascii')
print(line)
parm = line[line.index('('):line.index(')')].split(',')
host_data = '.'.join(parm[0:4])
port_data = int(float(parm[4]))*256+int(float(parm[5]))
s_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addr_data = (host_data, port_data)
print('Connecting to data', addr_data)
s_data.connect(addr_data)
print('Sending RETR command ...')
req = 'RETR {}\r\n'.format(path)
s_ctrl.sendall(req.encode('ascii'))
recv_data = s_ctrl.recv(1024)
line_end = recv_data.index(b'\r\n')
line = recv_data[0:line_end].decode('ascii')
print(line)
data = b''
while True:
  recv_data = s_data.recv(1024)
  if recv_data:
    data += recv_data
    print('Recieved', len(data), 'bytes ...')
  else:
    print('\n', data.decode('ascii'))
    s_data.close()
    s_ctrl.close()
    
