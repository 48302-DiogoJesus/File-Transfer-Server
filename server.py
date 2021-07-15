import socket
import time
import tqdm
import os
import sys
from _thread import *

# TCP socket
skt = socket.socket()
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5001
BUFFER_SIZE = 4096
SEPARATOR = ";"
thread_count = 0
server_path = 'Server_Storage'
user_capacity = 5
users_file = "users.txt"
# Dictionary key(user) -> list(password, ip)
users = {}


def start_listener():
    skt.bind((SERVER_HOST, SERVER_PORT))
    skt.listen(5)
    print(f"\n|------------- FTS --------------|\n"
          f"    [LISTENING] ON PORT : {SERVER_PORT}\n"
          f"|--------------------------------|\n")
    print(f"[!] Buffer Size : {BUFFER_SIZE}\n")
    wait_new_client()


def close_connection(client_socket):
    global thread_count
    thread_count -= 1
    client_socket.close()


def client_upload(client_socket, address):
    global thread_count
    user = get_user_from_ip(address[0])
    message_received = client_socket.recv(BUFFER_SIZE).decode()
    filename, file_size = message_received.split(SEPARATOR)
    filename = os.path.basename(filename)

    if not os.path.isdir(server_path + "/" + user):
        os.makedirs(server_path + "/" + user)
    new_file_path = server_path + "/" + user + "/" + filename
    file_size = int(file_size)
    print(f"[STARTING] \"{user}\" will start sending data.\n")
    progress = tqdm.tqdm(range(file_size), f"[RECEIVING] \"{filename}\" from \"{user}\" ", unit="B",
                         unit_scale=True, unit_divisor=1024, colour="yellow")
    with open(new_file_path, "wb") as f:
        bytes_received = 0
        while True:
            try:
                bytes_read = client_socket.recv(BUFFER_SIZE)
            except:
                print(f"\n[INTERRUPTED] \"{filename}\" from \"{user}\" was not successfully transferred.\n")
                f.close()
                progress.close()
                close_connection(client_socket)
                os.remove(new_file_path)
                break
            bytes_received += BUFFER_SIZE
            if not bytes_read:
                close_connection(client_socket)
                progress.close()
                if bytes_received >= file_size:
                    print(f"\n[DONE] \"{filename}\" has been received from \"{user}\"\n")
                    f.close()
                else:
                    print(f"\n[INCOMPLETE] \"{filename}\" from \"{user}\" was not successfully transferred.\n")
                    f.close()
                    os.remove(new_file_path)
                break
            # Write new file as we receive it
            f.write(bytes_read)
            progress.update(len(bytes_read))
    client_socket.close()


def client_download(client_socket, address):
    user = get_user_from_ip(address[0])
    while True:
        file = client_socket.recv(BUFFER_SIZE).decode()
        if file != "":
            break
    file_path = server_path + "/" + user + "/" + file
    if os.path.isfile(file_path) is False:
        # File does not exist on the server
        client_socket.sendall("\n[!] The file you requested does not exist".encode())
        return

    file_size = os.path.getsize(file_path)

    # Send the filename and filesize information first
    client_socket.sendall(f"{file_path}{SEPARATOR}{file_size}".encode())
    time.sleep(2)
    print()
    progress = tqdm.tqdm(range(file_size), f"[SENDING] {file_path} to {user}", unit="B", unit_scale=True,
                         unit_divisor=1024)
    with open(file_path, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                progress.close()
                print(f"\n[DONE] {file_path} was downloaded by {user}\n")
                break
            client_socket.sendall(bytes_read)
            progress.update(len(bytes_read))
    client_socket.close()


def client_list(client_socket, address):
    user = get_user_from_ip(address[0])
    user_path = server_path + "/" + user
    if os.path.isdir(user_path) is False:
        client_socket.sendall(str("Currently you have no files on the server.").encode())
        return
    client_socket.sendall(str(os.listdir(user_path)).encode())
    client_socket.close()


def wait_new_client():
    global thread_count
    print("\nWaiting for clients...")
    while True:
        if thread_count >= user_capacity:
            # Deny connections
            continue
        client_socket, address = skt.accept()
        # TESTING - REMOVE AFTER
        command = client_socket.recv(BUFFER_SIZE).decode().split(' ')
        if command[0] == "upload":
            action = client_upload
        elif command[0] == "download":
            action = client_download
        elif command[0] == "list":
            action = client_list
        elif command[0] == "check_login":
            if check_login(command[1], command[2]):
                client_socket.send("True".encode())
            else:
                client_socket.send("False".encode())
            continue
        elif command[0] == "get_ip_from_user":
            client_socket.send(get_ip_from_user(command[1]).encode())
            continue
        elif command[0] == "update_user_ip":
            client_socket.send(str(update_user_ip(command[1], command[2])).encode())
            continue
        else:
            continue
        # Thread the Client
        start_new_thread(action, (client_socket, address))
        thread_count += 1


# ------ USER MANIPULATION ------- #
def user_exists(username):
    if users.keys().__contains__(username):
        return True
    return False


def update_user_ip(username, new_ip):
    if not user_exists(username):
        return False
    users[username][1] = new_ip
    save_users_file()
    return True


def check_login(username, password):
    if not user_exists(username):
        return False
    if users[username][0] == password:
        return True
    return False


def get_user_from_ip(ip):
    for user in users.keys():
        if users[user][1] == ip:
            return user
    return None


def get_ip_from_user(username):
    if not user_exists(username):
        return None
    return users[username][1]


def extract_users_from_file():
    u_file = open(users_file, "r")
    users_info = u_file.readlines()
    for user_info in users_info:
        if user_info != "":
            users[user_info[:find_nth(user_info, SEPARATOR, 1)]] = \
                [user_info[find_nth(user_info, SEPARATOR, 1) + 1:find_nth(user_info, SEPARATOR, 2)],
                 user_info[find_nth(user_info, SEPARATOR, 2) + 1:len(user_info)].replace("\n", "")]


def save_users_file():
    u_file = open(users_file, "w")
    for user_info in users.keys():
        u_file.write(f"{user_info}{SEPARATOR}{users[user_info][0]}{SEPARATOR}{users[user_info][1]}\n")
    u_file.close()


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start


# SERVER INITIALIZATION
def server_init():
    global SERVER_PORT
    if len(sys.argv) > 1:
        SERVER_PORT = int(sys.argv[1])
    if not os.path.isdir(server_path):
        os.mkdir(server_path)
    if not os.path.isfile(users_file):
        open(users_file, "x")
    else:
        extract_users_from_file()

    # REMOVE AFTER
    for user in users:
        print(f"{user} -> {users[user]}")

    start_listener()


if __name__ == '__main__':
    try:
        server_init()
    finally:
        # IN CASE OF ERROR DURING THE EXECUTION
        save_users_file()
