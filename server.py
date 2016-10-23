import BaseHTTPServer
import os


class ServerException(Exception):
    """
    For internal error reporting.
    """
    pass


class BaseCase(object):
    """
    Parent for case handlers.
    """

    # HTTP status codes
    HTTP_NOT_FOUND = 404
    HTTP_INTERNAL_SERVER_ERROR = 500

    # How to display an error.
    error_page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    def handle_file(self, handler, full_path):
        try:
            with open(full_path, 'r') as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    def handle_error(self, handler, msg, status):
        content = self.error_page.format(path=handler.path, msg=msg)
        handler.send_content(content, status)

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        assert False, "Not implemented"

    def act(self, handler):
        assert False, "Not implemented."


class CaseNoFile(BaseCase):
    """
    File or directory does not exist.
    """

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        self.handle_error(handler, "'{0}' not found.".format(handler.path), self.HTTP_NOT_FOUND)


class CaseCgiFile(BaseCase):
    """
    Something runnable.
    """

    def run_cgi(self, handler):
        cmd = "python.exe " + handler.full_path
        child_stdin, child_stdout = os.popen2(cmd)
        child_stdin.close()
        data = child_stdout.read()
        child_stdout.close()
        handler.send_content(data)

    def test(self, handler):
        return os.path.isfile(handler.full_path) and handler.full_path.endswith('.py')

    def act(self, handler):
        self.run_cgi(handler)


class CaseExistingFile(BaseCase):
    """
    File exists.
    """

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)


class CaseDirectoryIndexFile(BaseCase):
    """
    Serve index.html page for a directory.
    """

    def test(self, handler):
        return os.path.isdir(handler.full_path) and os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))


class CaseDirectoryNoIndexFile(BaseCase):
    """
    Serve listing for a directory without an index.html page.
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

    def list_dir(self, handler, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            page = self.listing_page.format('\n'.join(bullets))
            handler.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(handler.path, msg)
            handler.handle_error(msg)

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.list_dir(handler, handler.full_path)


class CaseAlwaysFail(BaseCase):
    """
    Base case if nothing else worked.
    """

    def test(self, handler):
        return True

    def act(self, handler):
        self.handle_error(handler, "Unknown object '{0}'".format(handler.path), self.HTTP_INTERNAL_SERVER_ERROR)


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    If the requested path maps to a file, that file is served.
    If anything goes wrong, an error page is constructed.
    """

    cases = [
        CaseNoFile(),
        CaseCgiFile(),
        CaseExistingFile(),
        CaseDirectoryIndexFile(),
        CaseDirectoryNoIndexFile(),
        CaseAlwaysFail(),
    ]

    def do_GET(self):
        """
        Classify and handle request.
        :return:
        """
        # Figure out what exactly is begin requested.
        self.full_path = os.getcwd() + self.path

        # Figure out how to handle it.
        for case in self.cases:
            if case.test(self):
                case.act(self)
                break

    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == '__main__':
    server_address = ('', 8888)
    server = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    server.serve_forever()
