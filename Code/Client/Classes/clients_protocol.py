"""
The file of the protocol between the clients.
"""
import os
import hashlib


class ClientProtocol(object):
    """
    The class of the protocol between the clients.
    """

    @staticmethod
    def handle_request(request, yftf_files):
        """
        Handling a request from a downloader.
        """
        info_hash = request[0:40]
        piece_index = int(request[40:48])

        if info_hash not in yftf_files.keys():
            return None

        yftf_data = yftf_files[info_hash][0]
        shared_files_dir_path = yftf_files[info_hash][1]

        file_path = str()
        file_piece_index = int()

        pieces_counter = 0
        for shared_file_info in yftf_data["Info"]["Files"]:
            pieces_counter += len(shared_file_info["Pieces Hash"])

            if pieces_counter > piece_index:
                file_piece_index = piece_index - (pieces_counter - len(shared_file_info["Pieces Hash"]))
                file_path = shared_file_info["Path"]
                break

        if not file_path or not os.path.exists(shared_files_dir_path + file_path):
            return None

        shared_file = open(shared_files_dir_path + file_path, 'rb')
        shared_file.read(file_piece_index * yftf_data["Info"]["Piece Length"])
        data = shared_file.read(yftf_data["Info"]["Piece Length"])
        shared_file.close()

        return info_hash + data

    @staticmethod
    def request(info_hash, piece_index):
        """
        Request from a downloader to uploader.
        """
        return info_hash + str(piece_index).zfill(8)

    @staticmethod
    def handle_response(response, requests, yftf_files):
        """
        Handling a response from uploader.
        """
        info_hash = response[0:40]

        if info_hash not in yftf_files.keys() and info_hash not in requests.keys():
            return None

        yftf_data = yftf_files[info_hash][0]
        shared_files_dir_path = yftf_files[info_hash][1]
        pieces_index_requested = requests[info_hash]

        data = response[40:40 + yftf_data["Info"]["Piece Length"]]
        data_hash = hashlib.sha1(data).hexdigest()

        file_path = str()
        file_piece_index = int()
        piece_index = int()
        for piece_index in pieces_index_requested:
            pieces_counter = 0

            for shared_file_info in yftf_data["Info"]["Files"]:
                pieces_counter += len(shared_file_info["Pieces Hash"])

                if pieces_counter > piece_index:
                    file_piece_index = piece_index - (pieces_counter - len(shared_file_info["Pieces Hash"]))

                    if file_piece_index < 0 or file_piece_index > len(shared_file_info["Pieces Hash"]) - 1:
                        continue

                    if str(shared_file_info["Pieces Hash"][file_piece_index]) == data_hash or str(
                            shared_file_info["Hash"]) == data_hash:
                        file_path = str(shared_file_info["Path"])
                        break

            if file_path:
                break

        if not file_path:
            return None

        directories = file_path.split('\\')[0:-1]

        if not os.path.isdir(shared_files_dir_path + '\\' + yftf_data["Info"]["Name"]):
            os.makedirs(shared_files_dir_path + '\\' + yftf_data["Info"]["Name"])

        shared_files_dir_path += '\\' + yftf_data["Info"]["Name"]

        for directory in directories:
            if not os.path.isdir(shared_files_dir_path + '\\' + directory):
                os.makedirs(shared_files_dir_path + '\\' + directory)

        shared_file = open(shared_files_dir_path + file_path, 'wb')
        shared_file.seek(file_piece_index * yftf_data["Info"]["Piece Length"])
        shared_file.write(data)
        shared_file.close()

        return piece_index
