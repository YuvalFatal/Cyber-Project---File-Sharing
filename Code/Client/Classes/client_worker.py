from tornado.ioloop import IOLoop
from tornado import gen, queues
from tornado.httpclient import AsyncHTTPClient
import socket
import clients_protocol
import client_action


class ClientWorker(object):
    def __init__(self, yftf_files, num_workers, queue_size):
        self.yftf_files = yftf_files
        self.num_workers = num_workers
        self.queue_size = queue_size
        self.actions = {}
        self.queue = queues.Queue(self.queue_size)

        AsyncHTTPClient.configure(None, max_clients=self.num_workers)
        self.http_client = AsyncHTTPClient()

    def handle_response(self, response):
        if response.error:
            print "Error:", response.error
        else:
            if "Info-Hash" in response.headers.keys():
                data = list(self.actions[response.headers["Info-Hash"]].handle_response(self.yftf_files, response.headers))
            else:
                print "Error: Response not valid."
                return

            if data[0] is 0:
                print data[1]

            elif data[0] is 1:
                port = int(data[1])
                self.upload(response.headers["Info-Hash"], port)

            else:
                piece_index = data[1]
                uploader_ip = data[2]
                uploader_port = data[3]
                self.download(response.headers["Info-Hash"], piece_index, uploader_ip, uploader_port)

    @staticmethod
    def send(sock, data):
        length = len(data)
        length = str(length).zfill(8)

        sock.send(length + data)

    @staticmethod
    def receive(sock):
        length = int(sock.recv(8))
        data = ""

        while length != 0:
            data += sock.recv(1)
            length -= 1

        return data

    def download(self, info_hash, piece_index, uploader_ip, uploader_port):
        sock = socket.socket()
        sock.connect((uploader_ip, uploader_port))

        ClientWorker.send(sock, clients_protocol.ClientProtocol.request(info_hash, piece_index))

        clients_protocol.ClientProtocol.handle_response(ClientWorker.receive(sock), self.actions[info_hash].pieces_requested_index, self.yftf_files)

        self.actions[info_hash].pieces_requested_index[info_hash].remove(piece_index)
        self.actions[info_hash].finished_pieces_index.append(piece_index)

        sock.close()

    def upload(self, info_hash, port):
        self.actions[info_hash].port_range_in_use[port] = True

        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', port))

        server_socket.listen(1)

        (client_socket, client_address) = server_socket.accept()

        data = clients_protocol.ClientProtocol.handle_request(ClientWorker.receive(client_socket), self.yftf_files)

        ClientWorker.send(client_socket, data)

        self.actions[info_hash].port_range_in_use[port] = False

        client_socket.close()
        server_socket.close()

    @gen.coroutine
    def worker(self):
        while True:
            req = yield self.queue.get()

            try:
                yield self.http_client.fetch(req, self.handle_response)

            finally:
                self.queue.task_done()

    @gen.coroutine
    def do_work(self):
        for worker in range(self.num_workers):
            IOLoop.current().spawn_callback(self.worker)

        while True:
            if not self.actions:
                continue

            for info_hash, action in self.actions.iteritems():
                print info_hash
                req = action.request()

                if not req:
                    continue

                yield self.queue.put(req)

        yield self.queue.join()

    def start_client(self):
        IOLoop.current().run_sync(self.do_work)

    def add_action(self, command, yftf_files, info_hash, peer_id, peer_ip, port_range, num_workers, queue_size):
        print 'hi'
        self.yftf_files = yftf_files

        self.actions.update({info_hash: client_action.ClientAction(command, yftf_files, info_hash, peer_id, peer_ip, port_range, num_workers, queue_size)})
        print self.actions

    def stop_action(self, info_hash):
        del self.actions[info_hash]

        print self.actions
