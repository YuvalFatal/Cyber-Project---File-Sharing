import tornado.httpserver
import tornado.ioloop


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

http_server = tornado.httpserver.HTTPServer(handle_request)
http_server.listen(80)
tornado.ioloop.IOLoop.instance().start()