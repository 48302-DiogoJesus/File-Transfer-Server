# File-Transfer-Server
A simple file transfer server and client written in python.

## Features
-> Simple Usage
-> Connection established with tcp sockets (speeds arround 1,5Mb/s)
-> Suport for user authentication with username and password (users information stored server-side)
-> On Server-Side port forwarding is necessary if using the program outside LAN

## How it Works
The client files are stored in a folder on the server
The client can download, upload and list files from it's own server folder

## Install Dependencies
Note: Code written in python 3.9

### Client Dependencies
'<pip install requests>'

### Server Dependencies
'<pip install tqdm>'

## Program Usage

### Server
'<python server.py "serverport">' (Default port is 5001)

### Client
'<python client.py "serverip" "serverport">' (Default port is 5001)
