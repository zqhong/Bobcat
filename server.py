import BaseHTTPServer


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Handle HTTP requests by returning a fixed 'page'.
    """

    # Page to send back.
    page = '''\
<html>
<body>
<p>Hello, web!</p>
</body>
</html>
'''

    def do_GET(self):
        """
        Handle a GET request.
        :return:
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(self.page)))
        self.end_headers()
        self.wfile.write(self.page)


if __name__ == '__main__':
    serverAddress = ('', 8888)
    server = BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
