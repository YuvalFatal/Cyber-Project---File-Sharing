"""
Manging the client actions file.
"""
import hashlib
import json
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders
# from random import randint
import client_server_protocol


class ClientAction(object):
    """
    The class the manage the client actions.
    """

    def __init__(self, command, yftf_files, info_hash, peer_id, peer_ip, port_range, num_workers, queue_size):
        """
        Starting a new action.
        """

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

    def basic_request(self, headers):
        """
        Basic request to server.
        """
        return HTTPRequest(url=self.yftf_files[self.info_hash][0]["Announce"], method="GET",
                           headers=HTTPHeaders(headers), allow_nonstandard_methods=True)

    def find_unused_port(self):
        """
        Finding unused port.
        """
        port = int()

        for port, in_use in self.port_range_in_use.iteritems():
            if not in_use:
                return port

        return port

    def upload_request(self):
        """
        Upload request to server.
        """
        port = self.find_unused_port()

        if not port:
            return

        if len(self.finished_pieces_index) > 0:
            if len(self.finished_pieces_index) == 1:
                finished_piece = self.finished_pieces_index[0]
            else:
                finished_piece = self.finished_pieces_index

            req = self.basic_request(
                client_server_protocol.ClientServerProtocol.upload_request(self.info_hash, self.peer_id, self.peer_ip,
                                                                           port, finished_piece))
            self.finished_pieces_index = list()
        else:
            req = self.basic_request(
                client_server_protocol.ClientServerProtocol.upload_request(self.info_hash, self.peer_id, self.peer_ip,
                                                                           port))

        return req

    def request(self):
        """
        Getting the right request of the action.
        """
        if self.num_requests is 0 and self.command is 0:
            req = self.basic_request(
                client_server_protocol.ClientServerProtocol.start_new_download_request(self.info_hash, self.peer_id,
                                                                                       self.peer_ip, 0))

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

            req = self.basic_request(client_server_protocol.ClientServerProtocol.new_share_request(
                hashlib.sha1(json.dumps(self.yftf_files[self.info_hash][0])).hexdigest(), self.peer_id, self.peer_ip,
                port))
            req.body = json.dumps(self.yftf_files[self.info_hash][0])

            return req

        elif self.command is 2:
            return self.basic_request(
                client_server_protocol.ClientServerProtocol.finish_sharing_request(self.info_hash, self.peer_id,
                                                                                   self.peer_ip))

        elif self.command is 1:
            req = self.upload_request()

            if not req:
                return

            return req

        elif self.command is 0 and int(self.yftf_files[self.info_hash][0]["Info"]["Num Pieces"]) <= self.num_requests:
            req = self.upload_request()

            if not req:
                return

            return req

        else:
            # if randint(0, 1):
            #     req = self.upload_request()
            #
            #     if not req:
            #         return
            #
            #     return req
            #
            # else:
            if len(self.finished_pieces_index) > 0:
                if len(self.finished_pieces_index) == 1:
                    finished_piece = self.finished_pieces_index[0]
                else:
                    finished_piece = self.finished_pieces_index

                req = self.basic_request(
                    client_server_protocol.ClientServerProtocol.download_request(self.info_hash, self.peer_id,
                                                                                 self.peer_ip, self.num_requests,
                                                                                 finished_piece))
                self.finished_pieces_index = list()

                self.pieces_requested_index[self.info_hash] += [self.num_requests]
                self.num_requests += 1

                return req

            else:
                req = self.basic_request(
                    client_server_protocol.ClientServerProtocol.download_request(self.info_hash, self.peer_id,
                                                                                 self.peer_ip, self.num_requests))

                self.pieces_requested_index[self.info_hash] += [self.num_requests]
                self.num_requests += 1

                return req

    def handle_response(self, yftf_files, response_headers):
        """
        Handling the response from the server.
        """
        self.yftf_files = yftf_files

        return client_server_protocol.ClientServerProtocol.handle_response(self.yftf_files, self.pieces_requested_index,
                                                                           response_headers)
