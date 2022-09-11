# Importing packages
import socket
import os
import sys

# Defining the constants
HOST = sys.argv[1]
PORT = int(sys.argv[2])
RES = sys.argv[3]
FORMAT = "utf-8"
SIZE = 1024


def list_files(conn):
    conn.send(RES.encode(FORMAT))
    # List the files in the server directory
    files_on_server = conn.recv(SIZE).decode(FORMAT)
    print(files_on_server)

    # List cached files or empty cache message
    data = conn.recv(SIZE).decode(FORMAT)
    print(data)


def get_file(conn):
    conn.send(RES.encode(FORMAT))
    res = conn.recv(SIZE).decode(FORMAT)
    if res == "FNF":  # If the file was not found
        # Informs the client that the file was not found
        print(f"File {RES} does not exist in the server.")
    else:  # If the file is found
        dir_save = os.getcwd()+"/client_data/"
        if len(sys.argv) == 5:
            dir_save = sys.argv[4]
            if dir_save[len(dir_save) - 1] != '/':
                dir_save += '/'
            dir_save = os.getcwd() if dir_save == '.' or dir_save == './' or dir_save == '/' else dir_save

            if not os.path.isdir(dir_save):
                os.mkdir(dir_save)

        with open(os.path.join(dir_save, RES), 'wb') as file:
            print('Sending...')
            while True:
                filedata = conn.recv(4096)
                if not filedata:
                    break
                file.write(filedata)       
        print(f"\nFile {RES} saved.") # Informs the client that the file has been saved


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    if RES == "list":
        list_files(client_socket)
    else:
        get_file(client_socket)
    client_socket.close()
    print(f"\n[DISCONNECTED FROM THE SERVER]")


if __name__ == "__main__":
    main()
