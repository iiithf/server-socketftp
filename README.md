Basic FTP server implementation using sockets in Python.
<br>


## server

```bash
python server.py
# start server on port 2001, 2000 (data)

python server.py 3001
# start server on port 3001, 3000 (data)

python server.py 3001 3002
# start server on port 3001, 3002 (data)
```

## client

```bash
python client.py
# Get index.html from 127.0.0.1:2001

python client.py 127.0.0.1:3001
# Get index.html from 127.0.0.1:3001

python client.py 127.0.0.1:3001/server.py
# Get server.py from 127.0.0.1:3001
```
