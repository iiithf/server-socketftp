#!/usr/bin/env python
import socket
import selectors
import types
import sys
import os


# Create a TCP server
def tcp_server(addr, sel):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind(addr)
  s.setblocking(False)
  data = types.SimpleNamespace(type='conn', addr=addr, inb=b'', outb=b'', end=False, client=None)
  sel.register(s, selectors.EVENT_READ, data=data)
  s.listen()
  print('Listening on', addr)
  return s

# Accept FTP Control connection
def ftpctrl_accept(s):
  conn, addr = s.accept()
  print()
  print('Got a control connection', addr)
  conn.setblocking(False)
  data = types.SimpleNamespace(type='ctrl', addr=addr, inb=b'', outb=b'', end=False, client=None)
  events = selectors.EVENT_READ | selectors.EVENT_WRITE
  sel.register(conn, events, data=data)

# Service FTP Control connection
def ftpctrl_service(key, mask):
  conn = key.fileobj
  data = key.data
  if mask & selectors.EVENT_READ:
    recv_data = conn.recv(1024)
    if recv_data:
      data.inb += recv_data
      ftpctrl_process(data)
    else:
      print('Connection broke', data.addr)
      sel.unregister(conn)
      conn.close()
  if mask & selectors.EVENT_WRITE:
    if data.outb:
      print('Sending', len(data.outb), 'bytes to', data.addr)
      sent = conn.send(data.outb)
      data.outb = data.outb[sent:]

# Process FTP Control commands
def ftpctrl_process(data):
  while b'\r\n' in data.inb:
    line_end = data.inb.index(b'\r\n')
    line = data.inb[0:line_end].decode('ascii')
    print(line)
    data.inb = data.inb[line_end+2:]
    args = line.split(' ')
    if args[0]=='PASV':
      resp = '227 Entering Passive Mode (127,0,0,1,{},{})\r\n'.format(port_data//256, port_data%256)
      data.outb += resp.encode('ascii')
      shared.server = data
    elif args[0]=='RETR':
      if data.client is not None:
        data.client.end = True
      else:
        print('Error: No client to retrieve!')
        break
      path = args[1]
      if path[0:1]=='/':
        path = path[1:]
      if len(path)==0:
        path = 'index.html'
      if os.path.isfile(path):
        print('Retrieving', path)
        file_id = open(path, 'rb')
        data.client.outb += file_id.read()
        file_id.close()
        data.outb += b'226 Closing data connection\r\n'
      else:
        print('File', path, 'not found')
        data.outb += b'426 Connection closed; transfer aborted\r\n'

# Accept FTP Data connection
def ftpdata_accept(s):
  conn, addr = s.accept()
  print('Got a data connection', addr)
  conn.setblocking(False)
  data = types.SimpleNamespace(type='data', addr=addr, inb=b'', outb=b'', end=False, client=None)
  events = selectors.EVENT_READ | selectors.EVENT_WRITE
  sel.register(conn, events, data=data)
  if shared.server is None:
    sel.unregister(conn)
    conn.close()
  else:
    shared.server.client = data
    shared.server = None

# Service FTP Data connection
def ftpdata_service(key, mask):
  conn = key.fileobj
  data = key.data
  if mask & selectors.EVENT_READ:
    recv_data = conn.recv(1024)
    if recv_data:
      print('Recieved from', data.addr, recv_data)
    else:
      print('Connection broke', data.addr)
      sel.unregister(conn)
      conn.close()
  if mask & selectors.EVENT_WRITE:
    if data.outb:
      print('Sending', len(data.outb), 'bytes to', data.addr)
      sent = conn.send(data.outb)
      data.outb = data.outb[sent:]
    elif data.end:
      print('Closing connection', data.addr)
      sel.unregister(conn)
      conn.close()


# Main
port_ctrl = 2001
if len(sys.argv)>1:
  port_ctrl = int(float(sys.argv[1]))
port_data = port_ctrl-1
if len(sys.argv)>2:
  port_data = int(float(sys.argv[2]))
print('Starting FTP on {}, {} (data)'.format(port_ctrl, port_data))
shared = types.SimpleNamespace(server=None)
addr_ctrl = ('', port_ctrl)
addr_data = ('', port_data)
sel = selectors.DefaultSelector()
sel = selectors.DefaultSelector()
s_ctrl = tcp_server(addr_ctrl, sel)
s_data = tcp_server(addr_data, sel)
while True:
  events = sel.select(timeout=None)
  for key, mask in events:
    data = key.data
    if data.type=='conn':
      if data.addr==addr_ctrl:
        ftpctrl_accept(key.fileobj)
      else:
        ftpdata_accept(key.fileobj)
    elif data.type=='ctrl':
      ftpctrl_service(key, mask)
    elif data.type=='data':
      ftpdata_service(key, mask)
    else:
      print('Error: Unknown event!')
