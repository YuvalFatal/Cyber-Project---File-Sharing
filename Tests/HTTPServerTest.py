from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


def handle_request(request):
    for key in request.headers.keys():
        print key + ": " + request.headers[key]
    print request.body

    response = "HTTP/1.1 200 OK\r\n"

    body = "test"
    headers = {"YFT=d": "d", "Content-Length": len(body), "Connection": "keep-alive"}

    for header in headers:
        response += header + ": " + str(headers[header]) + "\r\n"

    response += "\r\n" + body
    print response

    request.write(response)
    request.finish()


def main(port):
    http_server = HTTPServer(handle_request)
    http_server.listen(port)
    IOLoop.instance().start()


if __name__ == '__main__':
    main(80)