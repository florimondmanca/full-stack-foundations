import logging
from http.server import BaseHTTPRequestHandler, HTTPServer


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith('/hello'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>Hello!</body></html>"
                self.wfile.write(output.encode())
                print(output)
            if self.path.endswith('/hola'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += (
                    "<html><body>"
                    "&#161;Hola! <a href='/hello'>Home</a>"
                    "</body></html>")
                self.wfile.write(output.encode())
                print(output)
        except IOError as e:
            self.send_error(404, f'File not found: {self.path}')


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print(f'Server running on port {port}.')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Stopping the server...')
        server.socket.close()


if __name__ == '__main__':
    main()
