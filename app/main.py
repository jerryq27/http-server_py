# Uncomment this to pass the first stage
import os
import sys
import socket
import threading


CRLF = '\r\n' # CarriageReturnLineFeed

def handle_request(connection, address):
    data = connection.recv(1024).decode() # Default decoding is utf-8

    request = data.split(CRLF)
    request_line = request[0]

    method, target, version = request_line.split(' ')

    if target == '/':
        response = b'HTTP/1.1 200 OK\r\n\r\n'
    elif '/echo' in target:
        echo_str = target[6:]

        response = CRLF.join([
            'HTTP/1.1 200 OK',
            'Content-Type: text/plain',
            f'Content-Length: {len(echo_str)}',
            f'{CRLF}{echo_str}',
        ])
        response = response.encode()
    elif '/user-agent' in target:
        for header in request:
            if header.lower().startswith('user-agent:'):
                user_agent = header.split(' ')[1]
                response = CRLF.join([
                    'HTTP/1.1 200 OK',
                    'Content-Type: text/plain',
                    f'Content-Length: {len(user_agent)}',
                    f'{CRLF}{user_agent}',
                ])
                response = response.encode()
    elif '/files' in target:
        program_name, arg_label, directory = sys.argv
        file_name = target[7:]

        file = os.path.join(directory, file_name)

        if os.path.isfile(file):
            with open(file, 'r') as requested_file:
                contents = requested_file.read()
            response = CRLF.join([
                'HTTP/1.1 200 OK',
                'Content-Type: application/octet-stream',
                f'Content-Length: {len(contents)}',
                f'{CRLF}{contents}'
            ])
            response = response.encode()
        else:
            response = b'HTTP/1.1 404 Not Found\r\n\r\n'
    else:
        response = b'HTTP/1.1 404 Not Found\r\n\r\n'

    connection.sendall(response)
    connection.close()


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        connection, address = server_socket.accept() # wait for client
        threading.Thread(target=handle_request, args=(connection, address), daemon=True).start()


if __name__ == "__main__":
    main()
