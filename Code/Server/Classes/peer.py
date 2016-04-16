class Peer(object):
    def __init__(self, peer_ip):
        self.peer_ip = peer_ip
        self.state = 0
        self.pieces = list()
        self.port = None

    def add_piece(self, index):
        if isinstance(index, list):
            self.pieces += index
            return

        self.pieces.append(index)

    def set_waiting_state(self, port):
        self.state = 1
        self.port = port

    def set_working_state(self):
        self.state = 0
        self.port = None

    def get_peer_ip(self):
        return self.peer_ip

    def get_state(self):
        return self.state

    def get_pieces(self):
        return self.pieces

    def get_port(self):
        return self.port

    def __str__(self):
        return ', '.join([self.peer_ip, str(self.state), str(self.pieces), str(self.port)])
