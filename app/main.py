import os
import sys
import socket
import threading


CRLF = '\r\n' # CarriageReturnLineFeed
VALID_COMPRESSION_SCHEMES = ['gzip']

def handle_request(connection, address):
    data = connection.recv(1024).decode() # Default decoding is utf-8

    header, body = data.split(CRLF*2)
    request_line = header.split(CRLF)[0]
    method, _, _ = request_line.split(' ')  

    method = method.lower()
    if method == 'get':
        print('GET')
        response = do_get(header, body)
    elif method == 'post':
        print('POST')
        response = do_post(header, body)
    else:
        print('Unsupported method: ' + method)
        response = b'HTTP/1.1 404 Not Found\r\n\r\n'

    connection.sendall(response)
    connection.close()

def do_get(header, body):
    header_lines = header.split(CRLF)
    request_line = header_lines[0]
    method, target, version = request_line.split(' ')

    response = b'HTTP/1.1 404 Not Found\r\n\r\n'

    if target == '/':
        response = b'HTTP/1.1 200 OK\r\n\r\n'
    elif '/echo' in target:
        echo_str = target[6:]

        # Check for compression header
        compression_argument = None
        for header_line in header_lines:
            if header_line.lower().startswith('accept-encoding:'):
                _, compression_argument = header_line.split(': ')
                break

        if compression_argument != None:
            schemes = compression_argument.split(', ')
            schemes = [x for x in schemes if x in VALID_COMPRESSION_SCHEMES]
            compression_argument = ', '.join(schemes)

            if compression_argument == '':
                compression_argument = None

        response_lines = [
            'HTTP/1.1 200 OK',
            'Content-Type: text/plain',
            f'Content-Length: {len(echo_str)}',
            f'{CRLF}{echo_str}',
        ]

        if compression_argument != None:
            response_lines = response_lines[:1] + [f'Content-Encoding: {compression_argument}'] + response_lines[1:]

        response = CRLF.join(response_lines)
        response = response.encode()
    elif '/user-agent' in target:
        for header_line in header_lines:
            if header_line.lower().startswith('user-agent:'):
                _, user_agent = header_line.split()
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
    
    return response

def do_post(header, body):
    header_lines = header.split(CRLF)
    request_line = header_lines[0]
    method, target, version = request_line.split(' ')
    
    response = b'HTTP/1.1 404 Not Found\r\n\r\n'

    if '/files' in target:
        program_name, arg_label, directory = sys.argv
        file_name = target[7:]

        file = os.path.join(directory, file_name)

        with open(file, 'w') as requested_file:
            requested_file.write(body)
        response = CRLF.join([
            'HTTP/1.1 201 Created',
            CRLF,
        ])
        response = response.encode()

    return response

def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)

    while True:
        connection, address = server_socket.accept() # wait for client
        threading.Thread(target=handle_request, args=(connection, address), daemon=True).start()


if __name__ == "__main__":
    main()
