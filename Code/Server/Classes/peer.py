"""
The file of the peer class.
"""


class Peer(object):
    """
    The class of the peer that contains all his data.
    """

    def __init__(self, peer_ip):
        """
        New peer constructor.
        """
        self.peer_ip = peer_ip
        self.state = 0
        self.pieces = list()
        self.port = None

    def add_piece(self, index):
        """
        Adding a finished piece.
        """
        if isinstance(index, list):
            self.pieces += index
            return

        self.pieces.append(index)

    def set_waiting_state(self, port):
        """
        Sets his state to waiting.
        """
        self.state = 1
        self.port = port

    def set_working_state(self):
        """
        Sets his state to working.
        """
        self.state = 0
        self.port = None

    def get_peer_ip(self):
        """
        Get peer ip.
        """
        return self.peer_ip

    def get_state(self):
        """
        Get peer state.
        """
        return self.state

    def get_pieces(self):
        """
        Get peer pieces.
        """
        return self.pieces

    def get_port(self):
        """
        Get peer listening port.
        """
        return self.port

    def __str__(self):
        """
        String of peer data.
        """
        return ', '.join([self.peer_ip, str(self.state), str(self.pieces), str(self.port)])
