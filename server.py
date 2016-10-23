import BaseHTTPServer


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Handle HTTP requests by returning a fixed 'page'.
    """

    # Page to send back.
    page = '''
<html>
<body>
<table>
<tr>  <td>Header</td>         <td>Value</td>          </tr>
<tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
<tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
<tr>  <td>Client port</td>    <td>{client_port}s</td> </tr>
<tr>  <td>Command</td>        <td>{command}</td>      </tr>
<tr>  <td>Path</td>           <td>{path}</td>         </tr>
</table>
</body>
</html>
'''

    def do_GET(self):
        """
        Handle a request by construing an HTML page that echoes the request back to the caller.
        :return:
        """
        page = self.create_page()
        self.send_page(page)

    def create_page(self):
        """
        Create an information page to send.
        :return:
        """
        values = {
            'date_time': self.date_time_string(),
            'client_host': self.client_address[0],
            'client_port': self.client_address[1],
            'command': self.command,
            'path': self.path
        }
        page = self.page.format(**values)
        return page

    def send_page(self, page):
        """
        Send the created page.
        :param page:
        :return:
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", len(page))
        self.end_headers()
        self.wfile.write(page)


if __name__ == '__main__':
    server_address = ('', 8888)
    server = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    server.serve_forever()
