from tornado.ioloop import IOLoop
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders
from tornado import queues
import time


NUM_WORKERS = 1 #Test!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
QUEUE_SIZE = 100
q = queues.Queue(QUEUE_SIZE)
AsyncHTTPClient.configure(None, max_clients=NUM_WORKERS)
http_client = AsyncHTTPClient()


def handle_request(response):
    if response.error:
        print "Error:", response.error
    else:
        print 'called'
        print response.body
        for key in response.headers.keys():
            print key + ": " + response.headers[key]


@gen.coroutine
def worker():
    while True:
        req = yield q.get()
        try:
            time.sleep(1) #Test!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            yield http_client.fetch(req, handle_request)
        except Exception:
            pass
        finally:
            q.task_done()


@gen.coroutine
def main():
    req = HTTPRequest(url="http://127.0.0.1:80", method="GET", body="test", headers=HTTPHeaders({"YFT": "test", "Connection": "keep-alive"}), allow_nonstandard_methods=True)

    for i in range(NUM_WORKERS):
        IOLoop.current().spawn_callback(worker)

    while True: #Test!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        yield q.put(req)
    yield q.join()


if __name__ == '__main__':
    IOLoop.current().run_sync(main)
