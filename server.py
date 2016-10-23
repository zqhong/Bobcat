import BaseHTTPServer
import os


class ServerException(Exception):
    """
    For internal error reporting.
    """
    pass


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Handle HTTP requests by returning a fixed 'page'.
    """

    # How to display an error.
    error_page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    def do_GET(self):
        """
        Classify and handle request.
        :return:
        """
        try:
            # Figure out what exactly is begin requested.
            full_path = os.getcwd() + self.path

            # It doesn't exists...
            if not os.path.exists(full_path):
                raise ServerException("'{0}' not found.".format(self.path))
            # it is a file
            elif os.path.isfile(full_path):
                self.handle_file(full_path)
            # it is something we don't handle.
            else:
                raise ServerException("Unknown object '{0}'".format(self.path))
        # Handle errors.
        except Exception as msg:
            self.handle_error(msg)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)

    def handle_error(self, msg):
        content = self.error_page.format(path=self.path, msg=msg)
        self.send_content(content)

    def send_content(self, content):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == '__main__':
    server_address = ('', 8888)
    server = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    server.serve_forever()
