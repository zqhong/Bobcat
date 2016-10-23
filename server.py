import BaseHTTPServer
import os


class ServerException(Exception):
    """
    For internal error reporting.
    """
    pass


class CaseNoFile(object):
    """
    File or directory does not exist.
    """

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found.".format(handler.path))


class CaseExistingFile(object):
    """
    File exists.
    """

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        handler.handle_file(handler.full_path)


class CaseDirectoryNoIndexFile(object):
    """
    Serve listing for a directory without an index.html page.
    """

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.list_dir(handler.full_path)


class CaseDirectoryIndexFile(object):
    """
    Serve index.html page for a directory.
    """

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.handle_file(self.index_path(handler))


class CaseAlwaysFail(object):
    """
    Base case if nothing else worked.
    """

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    If the requested path maps to a file, that file is served.
    If anything goes wrong, an error page is constructed.
    """

    cases = [
        CaseNoFile(),
        CaseExistingFile(),
        CaseDirectoryIndexFile(),
        CaseDirectoryNoIndexFile(),
        CaseAlwaysFail(),
    ]

    # How to display an error.
    error_page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    # Hwo to display a directory listing.
    listing_page = """\
        <html>
        <body>
        <ul>
        {0}
        </ul>
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
            self.full_path = os.getcwd() + self.path

            # Figure out how to handle it.
            for case in self.cases:
                if case.test(self):
                    case.act(self)
                    break
        # Handle errors.
        except Exception as msg:
            self.handle_error(msg)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'r') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)

    def handle_error(self, msg):
        content = self.error_page.format(path=self.path, msg=msg)
        self.send_content(content)

    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            page = self.listing_page.format('\n'.join(bullets))
            self.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)

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
