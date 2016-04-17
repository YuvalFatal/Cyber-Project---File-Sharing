import json
import os
import peer


class SharedFileTable(object):
    def __init__(self, info_hash, saved_tables_path, yftf_data=""):
        if os.path.isfile(os.path.join(saved_tables_path, info_hash + ".obj")):
            table_data = open(os.path.join(saved_tables_path, info_hash + ".obj"), 'rb')
            self.__dict__ = json.loads(table_data.read())
            table_data.close()

            for peer_id, peer_data in self.peers.iteritems():
                peer_obj = peer.Peer("")
                peer_obj.__dict__ = peer_data
                self.peers[peer_id] = peer_obj

            return

        self.saved_tables_path = saved_tables_path
        self.info_hash = info_hash
        self.yftf_data = yftf_data

        self.yftf_json = json.loads(self.yftf_data)

        self.num_pieces = self.yftf_json["Info"]["Num Pieces"]
        self.peers = dict()

    def get_info_hash(self):
        return self.info_hash

    def get_num_pieces(self):
        return self.num_pieces

    def add_peer(self, peer_id, peer_ip):
        self.peers.update({peer_id: peer.Peer(peer_ip)})

    def set_peer_waiting(self, peer_id, port):
        self.peers[peer_id].set_waiting_state(port)

    def set_peer_working(self, peer_id):
        self.peers[peer_id].set_working_state()

    def add_piece(self, peer_id, piece):
        self.peers[peer_id].add_piece(piece)

    def find_uploader(self, piece_index):
        for peer_id, peer_obj in self.peers.iteritems():
            if peer_obj.get_state():
                if piece_index in peer_obj.get_pieces():
                    port = peer_obj.get_port()
                    peer_obj.set_working_state()

                    return peer_obj.get_peer_ip(), port

        return None

    def remove_peer(self, peer_id):
        del self.peers[peer_id]

    def __str__(self):
        return ', '.join([self.yftf_data, self.info_hash, str(self.num_pieces), str(self.peers)])

    def __del__(self):
        table_data = open(os.path.join(self.saved_tables_path, self.info_hash + ".obj"), 'wb')
        for peer_id in self.peers.keys():
            self.peers[peer_id] = self.peers[peer_id].__dict__

        table_data.write(json.dumps(self.__dict__))
        table_data.close()
