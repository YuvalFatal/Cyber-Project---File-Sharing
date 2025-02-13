"""
The client worker file.
"""
from tornado.ioloop import IOLoop
from tornado import gen, queues
from tornado.httpclient import AsyncHTTPClient
import socket
import clients_protocol
import client_action
# import thread


class ClientWorker(object):
    """
    The class that manages the client worker.
    """

    def __init__(self, yftf_files, num_workers, queue_size):
        """
        Organize the client worker.
        """
        self.yftf_files = yftf_files

        self.num_workers = num_workers
        self.queue_size = queue_size
        self.queue = queues.Queue(self.queue_size)

        self.actions = {}

        AsyncHTTPClient.configure(None, max_clients=self.num_workers)
        self.http_client = AsyncHTTPClient()

    def handle_response(self, response):
        """
        Handling the response from the server.
        """
        if response.error:
            print "Error:", response.error
        else:
            if "Yft-Info-Hash" in response.headers.keys():
                data = list(
                    self.actions[response.headers["Yft-Info-Hash"]].handle_response(self.yftf_files, response.headers))
            elif "Yft-Error" in response.headers.keys():
                print response.headers["Yft-Error"]
                return
            else:
                print "Error: Response not valid"
                return

            if data[0] is 0:
                print data[1]

            elif data[0] is 1:
                port = int(data[1])
                # thread.start_new_thread(self.upload, (response.headers["Yft-Info-Hash"], port))
                self.upload(response.headers["Yft-Info-Hash"], port)

            else:
                piece_index = data[1]
                uploader_ip = data[2]
                uploader_port = data[3]
                # thread.start_new_thread(self.download,
                #                         (response.headers["Yft-Info-Hash"], piece_index, uploader_ip, uploader_port))
                self.download(response.headers["Yft-Info-Hash"], piece_index, uploader_ip, uploader_port)

    @staticmethod
    def send(sock, data):
        """
        Sending data to a client.
        """
        length = len(data)
        length = str(length).zfill(8)

        sock.send(length + data)

    @staticmethod
    def receive(sock):
        """
        Receiving data from a client.
        """
        length = int(sock.recv(8))
        data = ""
        while length != 0:
            data += sock.recv(1)
            length -= 1

        return data

    @gen.coroutine
    def download(self, info_hash, piece_index, uploader_ip, uploader_port):
        """
        Download the data from a client.
        """
        sock = socket.socket()
        sock.settimeout(30)
        sock.connect((uploader_ip, uploader_port))

        ClientWorker.send(sock, clients_protocol.ClientProtocol.request(info_hash, piece_index))

        clients_protocol.ClientProtocol.handle_response(ClientWorker.receive(sock),
                                                        self.actions[info_hash].pieces_requested_index, self.yftf_files)

        self.actions[info_hash].pieces_requested_index[info_hash].remove(piece_index)
        self.actions[info_hash].finished_pieces_index.append(piece_index)

        sock.close()

    @gen.coroutine
    def upload(self, info_hash, port):
        """
        Uploading data to a client.
        """
        self.actions[info_hash].port_range_in_use[port] = True

        server_socket = socket.socket()

        # temp_sock = socket.socket()
        #
        # if temp_sock.connect_ex(("127.0.0.1", port)) == 0:
        #     print "Error: Port is in use."
        #     temp_sock.close()
        #     return
        #
        # temp_sock.close()

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
        """
        Sending request to the server.
        """
        while True:
            req = yield self.queue.get()

            try:
                yield self.http_client.fetch(req, self.handle_response)

            finally:
                self.queue.task_done()

    @gen.coroutine
    def do_work(self):
        """
        Starting the workers.
        """
        for worker in range(self.num_workers):
            IOLoop.current().spawn_callback(self.worker)

        while True:
            if not self.actions:
                continue

            for info_hash, action in self.actions.iteritems():
                req = action.request()

                if not req:
                    continue

                yield self.queue.put(req)

        yield self.queue.join()

    def start_client(self):
        """
        Starting the client worker.
        """
        IOLoop.current().run_sync(self.do_work)

    def add_action(self, command, yftf_files, info_hash, peer_id, peer_ip, port_range, num_workers, queue_size):
        """
        Adding an action to the client worker.
        """
        self.yftf_files = yftf_files

        self.actions.update({info_hash: client_action.ClientAction(command, yftf_files, info_hash, peer_id, peer_ip,
                                                                   port_range, num_workers, queue_size)})

    def stop_action(self, info_hash):
        """
        Stopping an action.
        """
        del self.actions[info_hash]
