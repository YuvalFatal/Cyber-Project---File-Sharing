import hashlib
import json
import shared_file_table
import os


class ClientServerProtocol(object):
    def __init__(self, saved_tables_path):
        if os.path.isfile("data_save.obj"):
            data_save_file = open("data_save.obj", 'rb')
            saved_data = json.loads(data_save_file.read())
            data_save_file.close()

            self.saved_tables_path = saved_data["saved_tables_path"]
            yftf_files_info_hash = saved_data["yftf_files_info_hash"]

            self.yftf_files = dict()
            for info_hash in yftf_files_info_hash:
                self.yftf_files.update({info_hash: shared_file_table.SharedFileTable(info_hash, self.saved_tables_path)})

            return

        self.saved_tables_path = saved_tables_path
        self.yftf_files = dict()

    def handle_request(self, request_headers, request_body=""):
        if not request_headers:
            return {"YFT-Error": "You probably miss some headers"}

        if {"Yft-Peer-Id", "Yft-Peer-Status", "Yft-Upload-Piece", "Yft-Yftf-Hash", "Yft-Port", "Yft-Peer-Ip"}.issubset(set(request_headers.keys())):
            return self.handle_new_share(request_headers, request_body)

        if {"Yft-Info-Hash", "Yft-Peer-Id", "Yft-Peer-Ip", "Yft-Peer-Status", "Yft-Port"}.issubset(set(request_headers.keys())):
            if request_headers["Yft-Info-Hash"] not in self.yftf_files:
                return {"YFT-Error": "This file is not shared"}

            if request_headers["Yft-Peer-Status"] is str(2):
                self.remove_peer(request_headers)
                return

            if request_headers["Yft-Peer-Status"] is str(0):
                self.add_peer(request_headers)

            if "Yft-Finished-Piece-Index" in request_headers.keys():
                self.handle_finished_piece(request_headers)

            if "Yft-Request-Piece-Index" in request_headers.keys():
                return self.handle_downloader_request(request_headers)

            if {"Yft-Port", "Yft-Upload-Piece"}.issubset(set(request_headers.keys())) and request_headers["Yft-Upload-Piece"] is str(1):
                return self.handle_uploader_request(request_headers)

        return {"YFT-Error": "You probably miss some headers"}

    def remove_peer(self, request_headers):
        self.yftf_files[request_headers["Yft-Info-Hash"]].remove_peer(request_headers["Yft-Peer-Id"])

    def add_peer(self, request_headers):
        self.yftf_files[request_headers["Yft-Info-Hash"]].add_peer(request_headers["Yft-Peer-Id"], request_headers["Yft-Peer-Ip"])

    def handle_finished_piece(self, request_headers):
        self.yftf_files[request_headers["Yft-Info-Hash"]].add_piece(map(int, request_headers["Yft-Finished-Piece-Index"].split(', ')))

    def handle_downloader_request(self, request_headers):
        table = self.yftf_files[request_headers["Yft-Info-Hash"]]

        uploader_data = table.find_uploader(int(request_headers["Yft-Request-Piece-Index"]))

        if not uploader_data:
            return {"YFT-Info-Hash": table.get_info_hash(), "YFT-Error": "Could not find an uploader"}

        return {"YFT-Info-Hash": table.get_info_hash(), "YFT-Type": str(0), "YFT-ip": uploader_data[0], "YFT-Piece-Index": request_headers["Yft-Request-Piece-Index"], "YFT-Port": str(uploader_data[1])}

    def handle_uploader_request(self, request_headers):
        table = self.yftf_files[request_headers["Yft-Info-Hash"]]

        table.set_peer_waiting(request_headers["Yft-Peer-Id"], int(request_headers["Yft-Port"]))

        return {"YFT-Info-Hash": table.get_info_hash(), "YFT-Type": str(1), "YFT-Port": str(request_headers["Yft-Port"])}

    def handle_new_share(self, request_headers, request_body):
        if not request_body:
            return {"YFT-Error": "There is no yftf file in body"}

        if hashlib.sha1(request_body).hexdigest() != request_headers["Yft-Yftf-Hash"]:
            return {"Yft-Error": "yftf file corrupted"}

        yftf_json = json.loads(request_body)
        info_hash = hashlib.sha1(json.dumps(yftf_json["Info"])).hexdigest()

        if info_hash not in self.yftf_files.keys():
            table = shared_file_table.SharedFileTable(info_hash, self.saved_tables_path, request_body)
        else:
            return {"YFT-Info-Hash": info_hash, "YFT-Error": "File is already shared"}

        peer_id = request_headers["Yft-Peer-Id"]

        if request_headers["Yft-Peer-Status"] is str(0):
            table.add_peer(peer_id, request_headers["Yft-Peer-Ip"])
        else:
            return {"YFT-Info-Hash": info_hash, "YFT-Error": "Your status must be 0"}

        if request_headers["Yft-Upload-Piece"] is str(1):
            table.set_peer_waiting(peer_id, str(request_headers["Yft-Port"]))
        else:
            return {"YFT-Info-Hash": info_hash, "YFT-Error": "Your must share"}

        table.add_piece(peer_id, range(0, table.get_num_pieces()))

        self.yftf_files.update({info_hash: table})

        return {"YFT-Info-Hash": info_hash, "YFT-Type": str(1), "YFT-Port": str(request_headers["Yft-Port"])}

    def __del__(self):
        data_save_file = open("data_save.obj", 'wb')

        data_save_file.write(json.dumps({"saved_tables_path": self.saved_tables_path, "yftf_files_info_hash": self.yftf_files.keys()}))
        data_save_file.close()
