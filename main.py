import os
from time import sleep

import http.server
import socketserver

PORT = int(os.getenv('PORT','8000'))
Handler = http.server.SimpleHTTPRequestHandler



if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), Handler) as http:
        print("serving at port", PORT)
        http.serve_forever()