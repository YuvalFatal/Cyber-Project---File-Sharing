import hashlib
import json
import shared_file_table


class ClientServerProtocol(object):
    @staticmethod
    def handle_request(yftf_files, request_headers, saved_tables_path, request_body=""):
        if not request_headers:
            return {"YFT-Error": "You probably miss some headers"}

        if ["YFT-Peer-id", "YFT-Peer-Status", "YFT-Upload-Piece", "YFT-yftf-Hash"] in request_headers.keys():
            return ClientServerProtocol.handle_new_share(yftf_files, request_headers, request_body, saved_tables_path)

        if ["YFT-Info-Hash", "YFT-Peer-id", "YFT-Peer-ip", "YFT-Peer-Status"] in request_headers.keys():
            if request_headers["YFT-Info-Hash"] not in yftf_files:
                return {"YFT-Error": "This file is not shared"}

            if request_headers["YFT-Peer-Status"] is str(2):
                ClientServerProtocol.remove_peer(yftf_files, request_headers)
                return

            if request_headers["YFT-Peer-Status"] is str(0):
                ClientServerProtocol.add_peer(yftf_files, request_headers)

            if "YFT-Finished-Piece-Index" in request_headers.keys():
                ClientServerProtocol.handle_finished_piece(yftf_files, request_headers)

            if "YFT-Request-Piece-Index" in request_headers.keys():
                return ClientServerProtocol.handle_downloader_request(yftf_files, request_headers)

            if ["YFT-Port", "YFT-Upload-Piece"] in request_headers.keys() and request_headers["YFT-Upload-Piece"] is str(1):
                return ClientServerProtocol.handle_uploader_request(yftf_files, request_headers)

        return {"YFT-Error": "You probably miss some headers"}

    @staticmethod
    def remove_peer(yftf_files, request_headers):
        yftf_files[request_headers["YFT-Info-Hash"]].remove_peer(request_headers["YFT-Peer-id"])

    @staticmethod
    def add_peer(yftf_files, request_headers):
        yftf_files[request_headers["YFT-Info-Hash"]].add_peer(request_headers["YFT-Peer-id"], request_headers["YFT-Peer-ip"])

    @staticmethod
    def handle_finished_piece(yftf_files, request_headers):
        yftf_files[request_headers["YFT-Info-Hash"]].add_piece(map(int, request_headers["YFT-Finished-Piece-Index"].split(', ')))

    @staticmethod
    def handle_downloader_request(yftf_files, request_headers):
        table = yftf_files[request_headers["YFT-Info-Hash"]]

        uploader_data = table.find_uploader(int(request_headers["YFT-Request-Piece-Index"]))

        if not uploader_data:
            return {"YFT-Info-Hash": table.get_info_hash(), "YFT-Error": "Could not find an uploader"}

        return {"YFT-Info-Hash": table.get_info_hash(), "YFT-Type": str(0), "YFT-ip": uploader_data[0], "YFT-Piece-Index": request_headers["YFT-Request-Piece-Index"], "YFT-Port": str(uploader_data[1])}

    @staticmethod
    def handle_uploader_request(yftf_files, request_headers):
        table = yftf_files[request_headers["YFT-Info-Hash"]]

        table.set_peer_waiting(request_headers["YFT-Peer-id"], int(request_headers["YFT-Port"]))

        return {"YFT-Info-Hash": table.get_info_hash(), "YFT-Type": str(1)}

    @staticmethod
    def handle_new_share(yftf_files, request_headers, request_body, saved_tables_path):
        if not request_body:
            return {"YFT-Error": "There is no yftf file in body"}

        if hashlib.sha1(request_body).hexdigest() is not request_headers["YFT-yftf-Hash"]:
            return {"YFT-Error": "yftf file corrupted"}

        yftf_json = json.loads(request_body)
        info_hash = hashlib.sha1(yftf_json["Info"]).hexdigest()

        if info_hash not in yftf_files.keys():
            table = shared_file_table.SharedFileTable(info_hash, saved_tables_path, request_body)
        else:
            return {"YFT-Info-Hash": info_hash, "YFT-Error": "File is already shared"}

        peer_id = request_headers["YFT-Peer-id"]

        if request_headers["YFT-Peer-Status"] is str(0):
            table.add_peer(peer_id, request_headers["YFT-Peer-ip"])
        else:
            return {"YFT-Info-Hash": info_hash, "YFT-Error": "Your status must be 0"}

        if request_headers["YFT-Upload-Piece"] is str(1):
            table.set_peer_waiting(peer_id)
        else:
            return {"YFT-Info-Hash": info_hash, "YFT-Error": "Your must share"}

        table.add_piece(peer_id, range(0, table.get_num_pieces()))

        return {"YFT-Info-Hash": info_hash, "YFT-Type": str(1)}
