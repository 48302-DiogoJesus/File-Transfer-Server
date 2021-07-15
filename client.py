import socket
import time
import tqdm
import os
import sys
from requests import get

SERVER_IP = None
SERVER_PORT = 5001
SEPARATOR = ";"
BUFFER_SIZE = 4096


def start_client():
    global SERVER_PORT, SERVER_IP
    print("\n[|-|] File Transfer Server [|-|]\n")
    if len(sys.argv) == 1:
        print("[!] You need to specify the IP of the file server.")
        sys.exit(0)
    else:
        SERVER_IP = sys.argv[1]
    if is_online() is False:
        print(f"[!] \"{SERVER_IP}:{SERVER_PORT}\" is OFFLINE.\n\nClosing now...")
        sys.exit(0)
    if len(sys.argv) > 2:
        SERVER_PORT = int(sys.argv[2])
        print(f"[!] Using port {SERVER_PORT} to connect to the server.\n")
    else:
        print(f"[!] Since you didn't specify the server port, {SERVER_PORT} (default port) will be used.\n")
    while True:
        username = input("[?] Username : ")
        password = input("[?] Password : ")
        if send_command_to_server(f"check_login {username} {password}") == "True":
            break
        else:
            print(f"\n[!] Wrong credentials\n")
            continue
    current_ip = get_ip()
    previous_ip = send_command_to_server(f"get_ip_from_user {username}")
    if previous_ip != current_ip:
        print("\n[!] You are logging in with a different computer")
        send_command_to_server(f"update_user_ip {username} {get_ip()}")
        # SERVER RESPONSE print("\n[UPDATED] New IP registered successfully")

    # call main_menu here and there put the print
    main_menu(username)


def show_commands():
    print("\n|--AVAILABLE COMMANDS--|\n\n"
          "[-] help - Display this commands panel\n"
          "[-] upload - Upload a file from current folder\n"
          "[-] download - Download a file from your cloud\n"
          "[-] list - List files in your cloud.\n"
          "[-] exit - Close the program")


def send_command_to_server(command):
    server_socket = socket.socket()
    server_socket.connect((SERVER_IP, SERVER_PORT))
    server_socket.send(command.encode())
    return server_socket.recv(BUFFER_SIZE).decode()


def is_online():
    print(f"[!] Checking if {SERVER_IP}:{SERVER_PORT} is ONLINE...\n")
    sock = socket.socket()
    try:
        sock.connect((SERVER_IP, SERVER_PORT))
        sock.close()
        return True
    except:
        return False


def main_menu(username):
    print(f"\n|--Welcome {username}--|")
    show_commands()
    # MAIN LOOP
    while True:
        command = input("\n> Command : ")
        if command == "upload":
            file_to_upload = input("\n[!] The file must be in this directory\n[+] Filename : ")
            if file_to_upload != "":
                upload_file(file_to_upload)
        elif command == "help":
            show_commands()
        elif command == "download":
            download_file()
        elif command == "list":
            list_files()
        elif command == "exit":
            sys.exit(0)


def list_files():
    # create the client socket
    s = socket.socket()
    try:
        s.connect((SERVER_IP, SERVER_PORT))
        s.send(bytes("list", "ascii"))
    except:
        print("\nServer is either Offline or has reached it's simultaneous user capacity\n\nClosing now...")
        sys.exit(0)
    files = s.recv(BUFFER_SIZE).decode()
    print(f"\n[+] Files at your personal folder : {files}")


def upload_file(filename):
    # get the file size
    file_size = os.path.getsize(filename)
    # create the client socket
    s = socket.socket()
    try:
        s.connect((SERVER_IP, SERVER_PORT))
        s.send(bytes("upload", "ascii"))
    except:
        print("\nServer is either Offline or has reached it's simultaneous user capacity\n\nClosing now...")
        sys.exit(0)

    # send the filename and filesize
    s.send(f"{filename}{SEPARATOR}{file_size}".encode())
    time.sleep(2)
    print()
    progress = tqdm.tqdm(range(file_size), f"[UPLOADING] {filename}", unit="B", unit_scale=True, colour="Yellow", unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                progress.close()
                time.sleep(2)
                print(f"\n[DONE] {filename} was uploaded")
                break
            s.sendall(bytes_read)
            progress.update(len(bytes_read))
    s.close()


def download_file():
    while True:
        file_to_download = input("\n[?] Name of the file to download from server : ")
        if file_to_download != "":
            break

    # create the client socket
    s = socket.socket()
    try:
        s.connect((SERVER_IP, SERVER_PORT))
        s.send(bytes("download", "ascii"))
        s.send(bytes(file_to_download, "ascii"))
    except:
        print("\n[!] Server is either Offline or has reached it's user capacity\n\nClosing now...")
        sys.exit(0)

    received = s.recv(BUFFER_SIZE).decode()

    try:
        filename, file_size = received.split(SEPARATOR)
    except:
        print("\n[!] The file you requested does not exist")
        return

    # remove absolute path
    filename = os.path.basename(filename)

    file_size = int(file_size)
    print()
    progress = tqdm.tqdm(range(file_size), f"[RECEIVING] \"{filename}\" from server\" ", unit="B",
                         unit_scale=True, unit_divisor=1024, colour="yellow")
    # Recieve and save to destination
    with open(filename, "wb") as f:
        bytes_received = 0
        while True:
            # Read 4096 bytes from the socket
            try:
                bytes_read = s.recv(BUFFER_SIZE)
            except:
                # DONE
                print(f"\n[INTERRUPTED] \"{filename}\" was not successfully transferred\n")
                f.close()
                progress.close()
                s.close()
                os.remove(filename)
                break

            bytes_received += BUFFER_SIZE
            if not bytes_read:
                s.close()
                progress.close()
                if bytes_received >= file_size:
                    # DONE
                    print(f"\n[DONE] \"{filename}\" has been downloaded successfully\"")
                    f.close()
                else:
                    # NOT SUCCESSFUL TRANSFER
                    print()
                    print(f"\n[INTERRUPTED] \"{filename}\" was not successfully transferred\n")
                    f.close()
                    os.remove(filename)
                break
            # Write new file as we receive it
            f.write(bytes_read)
            progress.update(len(bytes_read))


def get_ip():
    ip = get('https://api.ipify.org').text
    return ip


if __name__ == '__main__':
    start_client()
