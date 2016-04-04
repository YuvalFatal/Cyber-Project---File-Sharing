from tornado.ioloop import IOLoop
from tornado import gen, queues
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import HTTPHeaders


class YFTClient(object):
    def __init__(self, num_workers, queue_size):
        self.num_workers = num_workers
        self.queue_size = queue_size

        self.queue = queues.Queue(self.queue_size)

        AsyncHTTPClient.configure(None, max_clients=self.num_workers)
        self.http_client = AsyncHTTPClient()

    @staticmethod
    def handle_response(response):
        if response.error:
            print "Error:", response.error #temp
        else:
            for key in response.headers.keys(): #temp
                print key + ": " + response.headers[key] #temp

    @gen.coroutine
    def worker(self):
        while True:
            req = yield self.queue.get()

            try:
                yield self.http_client.fetch(req, YFTClient.handle_response)
            except Exception:
                pass
            finally:
                self.queue.task_done()

    @gen.coroutine
    def do_work(self):
        req = HTTPRequest(url="http://127.0.0.1:80", method="GET", body="test", headers=HTTPHeaders({"YFT": "test", "Connection": "keep-alive"}), allow_nonstandard_methods=True)#temp

        for i in range(self.num_workers):
            IOLoop.current().spawn_callback(self.worker)

        while True: #temp
            yield self.queue.put(req) #temp
        yield self.queue.join() #temp

    def start_client(self):
        IOLoop.current().run_sync(self.do_work)
