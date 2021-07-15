# File-Transfer-Server
##### A simple file transfer server and client written in python.

## Features
* Simple Usage  
* Possibility for multiple users connected at the same time (uses Threading)  
* Connection established with tcp sockets (speeds arround 1,5Mb/s)  
* Suport for user authentication with username and password (users information stored server-side)  

## How it Works
The client files are stored in a folder on the server
The client can download, upload and list files from it's own server folder
##### Note: On Server-Side port forwarding is necessary when you want clients to connect from outside the server LAN  

## Install Dependencies
Note: Code written in python 3.9

### Client Dependencies
```
pip install requests
```

### Server Dependencies
```
pip install tqdm
```

## Program Usage

### Server
(Default port is 5001)

```
python server.py "serverport"
```

### Client
(Default port is 5001)

```
python client.py "serverip" "serverport"
```

