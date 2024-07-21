# Uncomment this to pass the first stage
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")
        
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept() # wait for client

    data = connection.recv(1024)
    data = data.decode() # Default decoding is utf-8

    request = data.split('\r\n')
    request_line = request[0]

    method, target, version = request_line.split(' ')

    if target != '/':
        response = b'HTTP/1.1 404 Not Found\r\n\r\n'
    else:
        response = b'HTTP/1.1 200 OK\r\n\r\n'

    connection.sendall(response)


if __name__ == "__main__":
    main()
