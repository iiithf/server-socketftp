#!/usr/bin/env python3
from urllib.parse import urlparse
import socket
import sys


# HTTP request format
class HttpRequest:
  headers = {}
  trailers = {}
  version = 1.1
  method = ''
  url = ''
  body = b''

# HTTP response format
class HttpResponse:
  headers = {}
  trailers = {}
  version = 1.1
  statusCode = 0
  statusMessage = ''
  body = b''

# Process HTTP head
def http_head(data):
  head_end = data.index(b'\r\n\r\n')
  if head_end<0:
    return None, data
  res = HttpResponse()
  head = data[0:head_end].decode('ascii')
  head_lines = head.split('\r\n')
  head_top = head_lines[0].split(' ')
  res.version = float(head_top[0].split('/')[1])
  res.statusCode = int(float(head_top[1]))
  res.statusMessage = head_top[2]
  for head_line in head_lines[1:]:
    header = head_line.split(': ')
    res.headers[header[0]] = header[1]
  return res, data[head_end+2:]

# Process HTTP body
def http_body(res, data):
  size = int(float(res.headers.get('Content-Length', '0')))
  if len(data)<size:
    return False, data
  res.body = data[0:size]
  return True, data[size:]

# Process HTTP request
def http_request(req):
  data = '{} {} HTTP/{}\r\n'.format(req.method, req.url, req.version)
  for key in req.headers:
    data += '{}: {}\r\n'.format(key, req.headers[key])
  data += '\r\n'
  return data.encode('ascii')+req.body


# Main
input_url = '127.0.0.1:8000'
if len(sys.argv)>1:
  input_url = sys.argv[1]
if 'http://' not in input_url:
  input_url = 'http://'+input_url
url = urlparse(input_url)
host = url.hostname
port = 80 if url.port is None else url.port
path = '/' if len(url.path)==0 else url.path
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
addr = (host, port)
print('Connecting to', addr)
s.connect(addr)
req = HttpRequest()
req.method = 'GET'
req.url = path
print('HTTP request', req.method, req.url)
s.sendall(http_request(req))
data = b''
res = None
while True:
  recv_data = s.recv(1024)
  data += recv_data
  print('Recieved', len(data), 'bytes ...')
  if res is None:
    res, data = http_head(data)
  if res:
    body_got, data = http_body(res, data)
    if body_got:
      print('Got a response', res.statusCode, res.statusMessage)
      print(res.body.decode('ascii'))
      s.close()
      break
