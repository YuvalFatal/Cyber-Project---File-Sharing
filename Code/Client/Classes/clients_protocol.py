import os
import hashlib


class ClientProtocol(object):
    @staticmethod
    def handle_request(request, yftf_files, shared_files_dir_path):
        info_hash = request[0:40]
        piece_index = int(request[40:48])

        if info_hash not in yftf_files.keys():
            return None

        yftf_data = yftf_files[info_hash]

        pieces_counter = -1
        for shared_file_info in yftf_data["Info"]["Files"]:
            pieces_counter += len(shared_file_info["Pieces Hash"])

            if pieces_counter >= piece_index:
                file_piece_index = piece_index - pieces_counter - len(shared_file_info["Pieces Hash"])
                file_path = shared_file_info["Path"]
                break

        if not file_path or not os.path.exists(file_path):
            return None

        shared_file = open(os.path.join(shared_files_dir_path, file_path), 'rb')
        shared_file.seek(file_piece_index * yftf_data["Info"]["Piece Length"])
        data = shared_file.read(yftf_data["Info"]["Piece Length"])
        shared_file.close()

        return info_hash + data

    @staticmethod
    def request(info_hash, piece_index):
        return info_hash + str(piece_index).zfill(8)

    @staticmethod
    def handle_response(response, requests, yftf_files, shared_files_dir_path):
        info_hash = response[0:40]

        if info_hash not in yftf_files.keys() or info_hash in requests.keys():
            return None

        yftf_data = yftf_files[info_hash]
        pieces_index_requested = requests[info_hash]

        data = response[40:40 + yftf_data["Info"]["Piece Length"]]
        data_hash = hashlib.sha1(data).hexdigest()

        for piece_index in pieces_index_requested:
            pieces_counter = -1

            for shared_file_info in yftf_data["Info"]["Files"]:
                pieces_counter += len(shared_file_info["Pieces Hash"])

                if pieces_counter >= piece_index:
                    file_piece_index = piece_index - pieces_counter - len(shared_file_info["Pieces Hash"])

                    if shared_file_info["Pieces Hash"][file_piece_index] is data_hash:
                        file_path = shared_file_info["Path"]
                        break

            if file_path:
                break

        if not file_path:
            return None

        shared_file = open(os.path.join(shared_files_dir_path, file_path), 'wb')
        shared_file.seek(file_piece_index * yftf_data["Info"]["Piece Length"])
        shared_file.write(data)
        shared_file.close()

        return piece_index
