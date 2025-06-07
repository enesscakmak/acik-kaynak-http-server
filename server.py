import socket
import os
import json
import mimetypes
import threading
import logging
import time
from urllib.parse import urlparse, unquote, parse_qs
from datetime import datetime

# Loglama yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)

class RouteHandler:
    def __init__(self):
        self.routes = {
            'GET': {},
            'POST': {}
        }
    
    def add_route(self, method, path, handler):
        self.routes[method][path] = handler
    
    def get_handler(self, method, path):
        return self.routes[method].get(path)

class HTTPServer:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.route_handler = RouteHandler()
        
        # MIME types için varsayılan tipleri ekle
        mimetypes.init()
        mimetypes.add_type('text/plain', '.txt')
        mimetypes.add_type('text/html', '.html')
        mimetypes.add_type('text/css', '.css')
        mimetypes.add_type('application/javascript', '.js')
        mimetypes.add_type('image/jpeg', '.jpg')
        mimetypes.add_type('image/png', '.png')
        mimetypes.add_type('application/json', '.json')
        
        # Varsayılan route'ları ekle
        self.route_handler.add_route('GET', '/api/hello', self.handle_api_hello)
        self.route_handler.add_route('GET', '/static/', self.handle_static_file)
        self.route_handler.add_route('POST', '/api/echo', self.handle_api_echo)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.info(f"Server running on http://{self.host}:{self.port}")

        while True:
            try:
                client_socket, address = self.server_socket.accept()
                logging.info(f"New connection from {address}")
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.start()
            except Exception as e:
                logging.error(f"Error accepting connection: {e}")

    def handle_client(self, client_socket, address):
        try:
            request_data = client_socket.recv(4096).decode('utf-8')
            if not request_data:
                return

            # Parse request
            request_lines = request_data.split('\n')
            request_line = request_lines[0].strip().split()
            
            if len(request_line) < 3:
                self.send_error(client_socket, 400, "Bad Request")
                return

            method, path, version = request_line
            
            # Parse URL and query parameters
            parsed_path = urlparse(path)
            path = unquote(parsed_path.path)
            query_params = parse_qs(parsed_path.query)
            
            # Get request body for POST requests
            body = ""
            if method == 'POST':
                # Find the empty line that separates headers from body
                empty_line_index = request_data.find('\r\n\r\n')
                if empty_line_index != -1:
                    body = request_data[empty_line_index + 4:]

            # Log request
            logging.info(f"{method} {path} from {address[0]}:{address[1]}")

            # DİNAMİK STATIC ROUTE
            if method == 'GET' and path.startswith('/static/'):
                self.handle_static_file(client_socket, path, query_params, body)
                return

            # Handle request
            handler = self.route_handler.get_handler(method, path)
            if handler:
                handler(client_socket, path, query_params, body)
            else:
                self.send_error(client_socket, 404, "Not Found")

        except Exception as e:
            logging.error(f"Error handling request: {e}")
            self.send_error(client_socket, 500, "Internal Server Error")
        finally:
            client_socket.close()

    def handle_api_hello(self, client_socket, path, query_params, body):
        response = {
            "message": "Hello, World!",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(client_socket, response)

    def handle_api_echo(self, client_socket, path, query_params, body):
        try:
            # Try to parse body as JSON
            body_data = json.loads(body) if body else {}
            response = {
                "message": "Echo response",
                "received_data": body_data,
                "query_params": query_params,
                "timestamp": datetime.now().isoformat()
            }
            self.send_json_response(client_socket, response)
        except json.JSONDecodeError:
            self.send_error(client_socket, 400, "Invalid JSON in request body")

    def handle_static_file(self, client_socket, path, query_params, body):
        # Remove /static/ prefix and get the file path
        file_path = os.path.join(os.getcwd(), path[1:])
        
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            logging.warning(f"File not found: {file_path}")
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
                logging.info(f"Served static file: {path}")
        except Exception as e:
            logging.error(f"Error reading file {path}: {e}")
            self.send_error(client_socket, 500, "Internal Server Error")

    def send_json_response(self, client_socket, data):
        content = json.dumps(data, indent=2).encode('utf-8')
        response = f"HTTP/1.1 200 OK\r\n"
        response += "Content-Type: application/json\r\n"
        response += f"Content-Length: {len(content)}\r\n"
        response += "\r\n"
        
        client_socket.send(response.encode('utf-8'))
        client_socket.send(content)
        logging.info("Sent JSON response")

    def send_error(self, client_socket, code, message):
        response = f"HTTP/1.1 {code} {message}\r\n"
        response += "Content-Type: text/plain\r\n"
        response += f"Content-Length: {len(message)}\r\n"
        response += "\r\n"
        response += message
        
        client_socket.send(response.encode('utf-8'))
        logging.warning(f"Sent error response: {code} {message}")

if __name__ == "__main__":
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Create sample static files
    with open('static/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>HTTP Server Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>HTTP Server Demo</h1>
    <div class="endpoint">
        <h2>GET /api/hello</h2>
        <p>Returns a JSON response with a greeting message.</p>
    </div>
    <div class="endpoint">
        <h2>POST /api/echo</h2>
        <p>Echoes back the JSON data sent in the request body.</p>
    </div>
</body>
</html>
        ''')
    
    server = HTTPServer()
    server.start() 