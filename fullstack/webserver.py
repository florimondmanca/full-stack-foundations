import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class WebServerHandler(BaseHTTPRequestHandler):

    form = (
        "<form method='POST' enctype='multipart/form-data' action='/hello'>"
        "<h2>What would you like me to say?</h2>"
        "<input name='message' type='text'>"
        "<input type='submit' value='Submit'>"
        "</form>"
    )

    def do_GET(self):
        try:
            if self.path.endswith('/hello'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                output = ""
                output += "<html><body>Hello!</body></html>"
                output += self.form
                self.wfile.write(bytes(output, 'utf-8'))
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
                output += self.form
                self.wfile.write(bytes(output, 'utf-8'))
                print(output)
        except IOError as e:
            self.send_error(404, f'File not found: {self.path}')

    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            ctype, pdict = cgi.parse_header(self.headers['content-type'])
            pdict['boundary'] = pdict['boundary'].encode()
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')
            message = messagecontent[0].decode()
            output = (
                "<html><body>"
                "<h2>Okay, how about this?</h2>"
                f"<h1>{message}</h1>"
                "</body></html>"
            )
            output += self.form
            self.wfile.write(bytes(output, 'utf-8'))
            print(output)
        except Exception as e:
            raise


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
