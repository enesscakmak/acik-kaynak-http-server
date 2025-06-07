import socket
import os
import json
import mimetypes
from urllib.parse import urlparse, unquote

class HTTPServer:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # MIME types için varsayılan tipleri ekle
        mimetypes.init()
        mimetypes.add_type('text/plain', '.txt')
        mimetypes.add_type('text/html', '.html')
        mimetypes.add_type('text/css', '.css')
        mimetypes.add_type('application/javascript', '.js')
        mimetypes.add_type('image/jpeg', '.jpg')
        mimetypes.add_type('image/png', '.png')
        mimetypes.add_type('application/json', '.json')

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server running on http://{self.host}:{self.port}")

        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Connection from {address}")
            self.handle_client(client_socket)

    def handle_client(self, client_socket):
        try:
            request_data = client_socket.recv(1024).decode('utf-8')
            if not request_data:
                return

            # Parse request
            request_lines = request_data.split('\n')
            request_line = request_lines[0].strip().split()
            
            if len(request_line) < 3:
                self.send_error(client_socket, 400, "Bad Request")
                return

            method, path, version = request_line
            
            if method != 'GET':
                self.send_error(client_socket, 405, "Method Not Allowed")
                return

            # Parse URL and handle different endpoints
            parsed_path = urlparse(path)
            path = unquote(parsed_path.path)

            if path == '/api/hello':
                self.handle_api_hello(client_socket)
            elif path.startswith('/static/'):
                self.handle_static_file(client_socket, path)
            else:
                self.send_error(client_socket, 404, "Not Found")

        except Exception as e:
            print(f"Error handling request: {e}")
            self.send_error(client_socket, 500, "Internal Server Error")
        finally:
            client_socket.close()

    def handle_api_hello(self, client_socket):
        response = {
            "message": "Hello, World!",
            "status": "success"
        }
        self.send_json_response(client_socket, response)

    def handle_static_file(self, client_socket, path):
        # Remove /static/ prefix and get the file path
        file_path = os.path.join(os.getcwd(), path[1:])
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self.send_error(client_socket, 404, "File Not Found")
            return

        try:
            with open(file_path, 'rb') as file:
                content = file.read()
                content_type, _ = mimetypes.guess_type(file_path)
                if content_type is None:
                    content_type = 'application/octet-stream'
                
                response = f"HTTP/1.1 200 OK\r\n"
                response += f"Content-Type: {content_type}\r\n"
                response += f"Content-Length: {len(content)}\r\n"
                response += "\r\n"
                
                client_socket.send(response.encode('utf-8'))
                client_socket.send(content)
        except Exception as e:
            print(f"Error reading file: {e}")
            self.send_error(client_socket, 500, "Internal Server Error")

    def send_json_response(self, client_socket, data):
        content = json.dumps(data).encode('utf-8')
        response = f"HTTP/1.1 200 OK\r\n"
        response += "Content-Type: application/json\r\n"
        response += f"Content-Length: {len(content)}\r\n"
        response += "\r\n"
        
        client_socket.send(response.encode('utf-8'))
        client_socket.send(content)

    def send_error(self, client_socket, code, message):
        response = f"HTTP/1.1 {code} {message}\r\n"
        response += "Content-Type: text/plain\r\n"
        response += f"Content-Length: {len(message)}\r\n"
        response += "\r\n"
        response += message
        
        client_socket.send(response.encode('utf-8'))

if __name__ == "__main__":
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Create a sample static file
    with open('static/hello.txt', 'w') as f:
        f.write('Hello from static file!')
    
    server = HTTPServer()
    server.start() 