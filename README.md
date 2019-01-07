Basic HTTP server implementation using sockets in Python.
<br>


## server

```bash
python server.py
# start server on port 8000

python server.py 2000
# start server on port 2000
```

## client

```bash
python client.py
# Get index.html from 127.0.0.1:8000

python client.py 127.0.0.1:2000
# Get index.html from 127.0.0.1:2000

python client.py 127.0.0.1:2000/client.py
# Get client.py from 127.0.0.1:2000
```
