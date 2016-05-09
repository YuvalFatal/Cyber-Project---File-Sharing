from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import client_server_protocol


class YFTServer(object):
    def __init__(self, listen_port, http_version, saved_tables_path):
        self.protocol = client_server_protocol.ClientServerProtocol(saved_tables_path)

        self.http_version = http_version
        self.http_server = HTTPServer(self.handle_request)

        self.http_server.listen(listen_port)

    def handle_request(self, request):
        headers = self.protocol.handle_request(request.headers, request.body)

        response = self.write_response(headers)

        request.write(response)
        request.finish()

    def write_response(self, headers, body=""):
        response = self.http_version + " 200 OK\r\n"

        for header in headers:
            response += header + ": " + str(headers[header]) + "\r\n"

        if "Content-Length" not in headers.keys() and body is not "":
            response += "Content-Length: " + str(len(body)) + "\r\n"

        response += "\r\n" + body

        return response

    def start_server(self):
        IOLoop.instance().start()


def main():
    listen_port = raw_input("What is the port you want to listen on?")
    http_version = "HTTP/1.1"
    saved_tables_path = raw_input("What is the path you want to save the tables to?")

    server = YFTServer(listen_port, http_version, saved_tables_path)

    server.start_server()


if __name__ == "__main__":
    main()
