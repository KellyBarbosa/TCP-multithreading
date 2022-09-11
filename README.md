# A tcp client-server multithreading

> **University:** UFRB - Universidade Federal do Recôncavo da Bahia <br/>
> **Professor:** Ramon Pereira Lopes <br/>
> **Student:** Gleice Kelly Barbosa Souza 

# Overview

This work requested the implementation of a server and a tcp client for file transfer. In addition, it was also requested the use of multithread, cache memory, lock and the implementation of an option to list the files present in cache memory.

The developed project can be divided into two options basically:

**Client requests list:** when the client requests a list of files, a list is sent to the client with the existing files in the server directory and the files present in the cache memory at the moment. If the cache is empty, a warning message is sent to the client.

**Client requests file:** when the client requests a file from the server, initially a check is performed if the file exists in cache memory or in the server directory. If it does not exist, a message is sent to the client informing that the file does not exist on the server. Otherwise, some steps are followed:
- If the file is present in cache memory, the file is sent to the client.
- If the file is not in cache memory:
  - If the file fits in cache memory and the cache has space available, the file is added to the cache and sent to the client.
  - If the file fits in cache memory and the cache has no space available, files that are already present in the cache are removed to make room for the new file. Then the file is added to the cache and sent to the client.
  - If the file size is greater than the maximum cache memory limit (64MB), the file is not added to the cache and is sent to the client.


# Running this application

### The first step is clone this project

```sh
$ git clone https://github.com/KellyBarbosa/TCP-multithreading.git
```

### Requirements
- You should have Python installed on your computer.

### Server

```sh
# Running the server
$ python3 tcp_server.py PORT

# Example
$ python3 tcp_server.py 9089
```

### Client

```sh
# Running the client to get a file
$ python3 tcp_client.py HOST PORT file_name dir_save

# Example
$ python3 tcp_client.py localhost 9089 file1.txt .

# Running the client to get the list
$ python3 tcp_client.py HOST PORT list

# Example
$ python3 tcp_client.py localhost 9089 list
```

# Design decisions

This project was developed using the Python language in version 3.9.7, in the Linux Mint system and in the Visual Studio Code IDE. This language was chosen because it natively supports the option of multithreading and lock (features that were requested in the requirements). In addition, it is also important to mention about the packages used during the development of the project:

- os
- sys
- socket
- threading

### Brief description of the usage of each package:

- The *os* package was used for managing directories, such as checking for existence and creating new directories, for example.
- The *sys* package was used to retrieve the information passed at the time of server and client execution.
- The *socket* packet was used to create the TCP communication between the client and the server.
- The *threading* package was used to manage multithreading and lock.

## Multithreading Management

After being started, the server was executed in an infinite loop to be always available to receive new connections from clients, and for each new one that started a new connection with the server, a new thread was created to manage requests from this client.

``` python
while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(
            target=newClientConnection, args=(conn, addr, lock))
        thread.start()
```
An example of how multithreading works in this project can be seen below.

In the illustration above, three clients connect simultaneously to the server and they all make requests at the same time. It can also be seen that all of them have their requests met.

## Lock

To lock the files, the *Semaphore* functionality provided by the threading library was used. Through this functionality, *acquire* was used to lock the file and *release* to unlock the file.

```python
lock = threading.Semaphore()

# lock file
lock.acquire()

# unlock file
lock.release()
```

## Cache management

To manage the cache, the dictionaries functionality of the python language was used. In which, the file name and its contents are saved in this cache. When the client requests a file, if the file size is smaller than the cache size and the cache has available space, it is added to the cache. If the file size is smaller than the cache size and the cache does not have available space, some files are removed from the cache until enough space is available for this new file. To perform this removal, the FIFO (first in first out) strategy is used, in this way, it can be guaranteed that the data to be removed will always be the oldest in the cache.