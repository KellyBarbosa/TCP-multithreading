# Importing packages
import os
import socket
import threading
import sys

# Defining the constants
HOST = "localhost"
PORT = int(sys.argv[1])
SIZE = 1024
FORMAT = "utf-8"
DIRECTORY = os.getcwd()+"/server_data/"
MAX_CACHE_SIZE = 67108864

cache = dict()
cache_actual_size: int

# Returns the current cache size
def cacheActualSize(cache: dict):
    size = 0
    for key in cache:
        size += sizeData(cache[key])
    return size

# Returns the size of the data
def sizeData(data):
    size = 0
    for line in data:
        size += line.__sizeof__()
    return size

# Method that controls the connection to the client
def newClientConnection(conn, addr, lock):
    print(f"[+][NEW CONNECTION] The client {addr} is connected now.")

    while True:
        data = conn.recv(SIZE).decode(FORMAT)
        files = os.listdir(DIRECTORY)

        # If the command is list
        if data == "list":  
            print(f"The client {addr} is checking cached files.")
            server_socket_msg = "[FILES IN THE SERVER DIRECTORY]:\n"
            server_socket_msg += "\n".join(f for f in files)
            server_socket_msg += "\n\n===============================\n"           
            conn.send(server_socket_msg.encode(FORMAT)) # Sends to the client a list of the files available in the server directory

            if len(cache) == 0:             
                conn.send('The cache is empty.'.encode(FORMAT)) # Informs the client that the cache is empty
            else:
                server_socket_msg = "[CACHED FILES]:\n"
                server_socket_msg += "\n".join(k for k in cache.keys())            
                conn.send(server_socket_msg.encode(FORMAT)) # Sends a list of files available in the cache to the client
                print(f"List of cached files sent to the client {addr}.")
            break

        else:  # If the client wants to fetch a file
            filename = data
            print(f'Client {addr} is requesting file {filename}.')
            # Checks if file exists in cache or server directory
            if filename in files or filename in cache:               
                conn.send(("FF").encode(FORMAT)) # FF = File found
                if filename in cache:  # If the file is cached
                    for data in cache[filename]:
                        conn.send(data) 
                    print(f"Cache hit. File {filename} sent to the client.")
                    break
                else:  # If the file is not cached
                    lock.acquire()
                    with open(os.path.join(DIRECTORY, filename), 'rb') as file:
                        while True:
                            bytes_read = file.read(4096)
                            if not bytes_read:
                                break
                            conn.send(bytes_read)
                    print(f"Cache miss. File {filename} sent to the client.")

                    with open(os.path.join(DIRECTORY, filename), 'rb') as file:
                        data = file.readlines()
                        dataSize = sizeData(data)

                        cache_actual_size = cacheActualSize(cache)

                        keys = []
                        if not dataSize > MAX_CACHE_SIZE:
                            while (cache_actual_size+dataSize) > MAX_CACHE_SIZE:
                                for k in cache:
                                    keys.append(k)

                                cache_actual_size -= sizeData(cache[keys[0]])
                                cache.pop(keys[0])
                                keys.pop(0)

                            cache.update({filename: data})
                    lock.release()
                    break
            else:  # If the file is not found
                print(f"File {filename} does not exist.")            
                conn.send(("FNF").encode(FORMAT)) # FNF = File not found
                break

    print(f"[-][DISCONNECTED] The client {addr} has disconnected.\n")
    conn.close()

def main():
    print("==================================================")
    print("[STARTING] Server is starting...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    lock = threading.Semaphore()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}.")
    print("==================================================\n")
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(
            target=newClientConnection, args=(conn, addr, lock))
        thread.start()


if __name__ == "__main__":
    main()
