class ClientServerProtocol(object):
    @staticmethod
    def new_share_request(info_hash, peer_id, peer_ip, port):
        return {"YFT-Peer-id": peer_id, "YFT-Peer-ip": peer_ip, "YFT-yftf-Hash": info_hash, "YFT-Peer-Status": str(0),
                "YFT-Upload-Piece": str(1), "YFT-Port": str(port)}

    @staticmethod
    def download_request(info_hash, peer_id, peer_ip, request_piece_index, finished_piece_index=None):
        headers = ClientServerProtocol.basic_request(info_hash, peer_id, peer_ip)
        headers.update({"YFT-Peer-Status": str(1), "YFT-Request-Piece-Index": str(request_piece_index)})

        if finished_piece_index:
            if isinstance(finished_piece_index, list):
                finished_piece_index = ', '.join(finished_piece_index)
            else:
                finished_piece_index = str(finished_piece_index)

            headers.update({"YFT-Finished-Piece-Index": finished_piece_index})

        return headers

    @staticmethod
    def upload_request(info_hash, peer_id, peer_ip, port, finished_piece_index=None):
        headers = ClientServerProtocol.basic_request(info_hash, peer_id, peer_ip)
        headers.update({"YFT-Peer-Status": str(1), "YFT-Upload-Piece": str(1), "YFT-Port": str(port)})

        if finished_piece_index:
            if isinstance(finished_piece_index, list):
                finished_piece_index = ', '.join(finished_piece_index)
            else:
                finished_piece_index = str(finished_piece_index)

            headers.update({"YFT-Finished-Piece-Index": finished_piece_index})

        return headers

    @staticmethod
    def start_new_download_request(info_hash, peer_id, peer_ip, request_piece_index):
        headers = ClientServerProtocol.basic_request(info_hash, peer_id, peer_ip)
        headers.update({"YFT-Peer-Status": str(0), "YFT-Request-Piece-Index": str(request_piece_index)})

        return headers

    @staticmethod
    def finish_sharing_request(info_hash, peer_id, peer_ip):
        headers = ClientServerProtocol.basic_request(info_hash, peer_id, peer_ip)
        headers.update({"YFT-Peer-Status": str(2)})

        return headers

    @staticmethod
    def basic_request(info_hash, peer_id, peer_ip):
        return {"YFT-Info-Hash": info_hash, "YFT-Peer-id": peer_id, "YFT-Peer-ip": peer_ip}

    @staticmethod
    def handle_response(yftf_files, pieces_requested_index, response_headers):
        if "Yft-Info-Hash" not in response_headers.keys() or response_headers["Yft-Info-Hash"] not in yftf_files.keys():
            return 0, "ERROR: Response not valid"

        yftf_json = yftf_files[response_headers["Yft-Info-Hash"]][0]

        if "Yft-Error" in response_headers.keys():
            return 0, yftf_json["Info"]["Name"] + " - ERROR:" + response_headers["Yft-Error"]

        if "Yft-Type" not in response_headers.keys():
            return 0, yftf_json["Info"]["Name"] + " - ERROR: Header is missing"

        if response_headers["Yft-Type"] is str(1):
            return 1, response_headers["Yft-Port"]

        if response_headers["Yft-Info-Hash"] not in pieces_requested_index.keys():
            return 0, yftf_json["Info"]["Name"] + " - ERROR: You didn't requested from this file"

        if int(response_headers["Yft-Piece-Index"]) not in pieces_requested_index[response_headers["Yft-Info-Hash"]]:
            return 0, yftf_json["Info"]["Name"] + " - ERROR: You didn't requested this piece"

        return 2, int(response_headers["Yft-Piece-Index"]), response_headers["Yft-Ip"], int(
            response_headers["Yft-Port"])
