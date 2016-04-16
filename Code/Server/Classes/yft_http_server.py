from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


class YFTHTTPServer(object):
    def __init__(self, listen_port, http_version):
        self.http_version = http_version
        self.http_server = HTTPServer(self.handle_request)

        self.http_server.listen(listen_port)

    def handle_request(self, request):
        for key in request.headers.keys(): #temp
            print key + ": " + request.headers[key] #temp

        body = "test" #temp
        headers = {"YFT=d": "d", "Connection": "keep-alive"} #temp

        response = self.write_response(headers, body)

        request.write(response)
        request.finish()

    def write_response(self, headers={}, body=""):
        response = self.http_version + " 200 OK\r\n" #temp

        for header in headers:
            response += header + ": " + str(headers[header]) + "\r\n"

        if "Content-Length" not in headers.keys() and body is not "":
            response += "Content-Length: " + str(len(body)) + "\r\n"

        response += "\r\n" + body

        return response

    def start_server(self):
        IOLoop.instance().start()
