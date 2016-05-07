from tornado.ioloop import IOLoop
from tornado import gen, queues
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import HTTPHeaders
import client_server_protocol
from random import randint
import socket
import clients_protocol
import hashlib
import json


class ClientWorker(object):
    def __init__(self, command, yftf_files, info_hash, peer_id, peer_ip, port_range, num_workers, queue_size):
        self.peer_id = peer_id
        self.peer_ip = peer_ip
        self.port_range_in_use = dict(zip(port_range, [False] * len(port_range)))

        self.yftf_files = yftf_files
        self.info_hash = info_hash
        self.pieces_requested_index = dict()
        self.finished_pieces_index = list()

        self.num_workers = num_workers
        self.queue_size = queue_size

        self.num_requests = 0
        self.first_uploader = 0
        self.command = command

        self.queue = queues.Queue(self.queue_size)

        AsyncHTTPClient.configure(None, max_clients=self.num_workers)
        self.http_client = AsyncHTTPClient()

    def stop_upload(self):
        IOLoop.current().close()

    def handle_response(self, response):
        if response.error:
            print "Error:", response.error
        else:
            data = list(client_server_protocol.ClientServerProtocol.handle_response(self.yftf_files, self.pieces_requested_index, response.headers))

            if data[0] is 0:
                print data[1]

            elif data[0] is 1:
                port = int(data[1])
                self.upload(port)

            else:
                piece_index = data[1]
                uploader_ip = data[2]
                uploader_port = data[3]
                self.download(piece_index, uploader_ip, uploader_port)

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

    def download(self, piece_index, uploader_ip, uploader_port):
        sock = socket.socket()
        sock.connect((uploader_ip, uploader_port))

        ClientWorker.send(sock, clients_protocol.ClientProtocol.request(self.info_hash, piece_index))

        clients_protocol.ClientProtocol.handle_response(ClientWorker.receive(sock), self.pieces_requested_index, self.yftf_files)

        self.pieces_requested_index[self.info_hash].remove(piece_index)
        self.finished_pieces_index.append(piece_index)

        sock.close()

    def upload(self, port):
        self.port_range_in_use[port] = True

        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', port))

        server_socket.listen(1)

        (client_socket, client_address) = server_socket.accept()

        data = clients_protocol.ClientProtocol.handle_request(ClientWorker.receive(client_socket), self.yftf_files)

        ClientWorker.send(client_socket, data)

        self.port_range_in_use[port] = False

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

    def find_unused_port(self):
        port = int()

        for port, in_use in self.port_range_in_use.iteritems():
            if not in_use:
                return port

        return port

    def upload_request(self):
        port = self.find_unused_port()

        if not port:
            return

        if len(self.finished_pieces_index) > 0:
            req = self.basic_request(client_server_protocol.ClientServerProtocol.upload_request(self.info_hash, self.peer_id, self.peer_ip, port, self.finished_pieces_index))
            self.finished_pieces_index = list()
        else:
            req = self.basic_request(client_server_protocol.ClientServerProtocol.upload_request(self.info_hash, self.peer_id, self.peer_ip, port))

        return req

    def basic_request(self, headers):
        return HTTPRequest(url=self.yftf_files[self.info_hash][0]["Announce"], method="GET", headers=HTTPHeaders(headers), allow_nonstandard_methods=True)

    def request(self):
        if self.num_requests is 0 and self.command is 0:
            req = self.basic_request(client_server_protocol.ClientServerProtocol.start_new_download_request(self.info_hash, self.peer_id, self.peer_ip, 0))

            if self.info_hash not in self.pieces_requested_index:
                self.pieces_requested_index.update({self.info_hash: []})

            self.pieces_requested_index[self.info_hash] += [self.num_requests]
            self.num_requests += 1

            return req

        elif self.first_uploader is 0 and self.command is 1:
            port = self.find_unused_port()

            if not port:
                return

            self.first_uploader += 1

            req = self.basic_request(client_server_protocol.ClientServerProtocol.new_share_request(hashlib.sha1(json.dumps(self.yftf_files[self.info_hash][0])).hexdigest(), self.peer_id, self.peer_ip, port))
            req.body = json.dumps(self.yftf_files[self.info_hash][0])

            return req

        elif self.command is 2:
            return self.basic_request(client_server_protocol.ClientServerProtocol.finish_sharing_request(self.info_hash, self.peer_id, self.peer_ip))

        elif self.command is 1:
            req = self.upload_request()

            if not req:
                return

            return req

        elif self.command is 0 and int(self.yftf_files[self.info_hash][0]["Info"]["Num Pieces"]) >= self.num_requests:
            req = self.upload_request()

            if not req:
                return

            return req

        else:
            if randint(0, 1):
                req = self.upload_request()

                if not req:
                    return

                return req

            else:
                if len(self.finished_pieces_index) > 0:
                    req = self.basic_request(client_server_protocol.ClientServerProtocol.download_request(self.info_hash, self.peer_id, self.peer_ip, self.num_requests, self.finished_pieces_index))
                    self.finished_pieces_index = list()

                    return req

                else:
                    req = self.basic_request(client_server_protocol.ClientServerProtocol.download_request(self.info_hash, self.peer_id, self.peer_ip, self.num_requests))

                    self.pieces_requested_index[self.info_hash] += [self.num_requests]
                    self.num_requests += 1

                    return req

    @gen.coroutine
    def do_work(self):
        for worker in range(self.num_workers):
            IOLoop.current().spawn_callback(self.worker)

        while True:
            req = self.request()

            if not req:
                continue

            yield self.queue.put(req)

        yield self.queue.join()

    def start_client(self):
        IOLoop.current().run_sync(self.do_work)
