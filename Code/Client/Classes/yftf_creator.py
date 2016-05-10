"""
Containing the yftf creator class.
"""
import os
import json
import hashlib


class YftfCreator(object):
    """
    Class that makes the yftf file for the file/s you want to share.
    """

    def __init__(self, path, yftf_path, tracker_url):
        """
        Creating the yftf file.
        """
        self.piece_length = 262144
        self.is_file = False
        self.num_pieces = 0
        self.tracker_url = tracker_url

        exists = self.is_exist(path, yftf_path)

        if exists[0]:
            self.path = path
            self.create_yftf(yftf_path)
        else:
            print "ERROR: " + exists[1]

    def is_exist(self, path, yftf_path):
        """
        Checking if the file or directory exists.
        """
        if os.path.isfile(path):
            self.is_file = True

        if not os.path.isdir(yftf_path):
            return False, "Saving path location not exist!"

        if not os.path.isdir(path) and not self.is_file:
            return False, "File or directory not exist!"

        return True, ''

    def get_data(self):
        """
        Organizing all the data that needs for the yftf file.
        """
        yftf_data = dict()
        yftf_data['Announce'] = self.tracker_url
        yftf_data['Info'] = dict()

        yftf_data['Info']['Name'] = self.path.split('\\')[-1]

        if self.is_file:
            yftf_data['Info']['Name'] = self.path.split('\\')[-1]

        yftf_data['Info']['Piece Length'] = self.piece_length

        files_data = self.get_files_info(self.path)

        if len(files_data) is 1:
            yftf_data['Info'].update(files_data[0])
            return yftf_data

        yftf_data['Info']['Files'] = files_data

        yftf_data['Info']['Num Pieces'] = self.num_pieces

        return yftf_data

    def create_yftf(self, path):
        """
        Creating the yftf file.
        """
        yftf_data = self.get_data()

        if self.is_file:
            yftf = open(os.path.join(path, ''.join(yftf_data['Info']['Name'].split('.')[:-1]) + '.yftf'), 'w')
        else:
            yftf = open(os.path.join(path, yftf_data['Info']['Name'] + '.yftf'), 'w')

        yftf.write(json.dumps(yftf_data))

    def get_files_info(self, path):
        """
        Organizing all the files info.
        """
        files = []

        if self.is_file:
            files.append(self.get_file_info(path))
            return files

        for new_path in os.listdir(path):
            new_path = path + '\\' + new_path

            if os.path.isdir(new_path):
                dir_files = self.get_files_info(new_path)
                files += dir_files
                continue

            files.append(self.get_file_info(new_path))

        return files

    def get_file_info(self, path):
        """
        Organizing all the file info.
        """
        file_info = dict()
        file_data = open(path, 'rb').read()

        if not self.is_file:
            file_info['Path'] = path.replace(self.path, '').decode('iso-8859-8').encode('utf-8')

        file_info['Length'] = os.path.getsize(path)
        file_info['Hash'] = YftfCreator.get_data_hash(file_data)
        file_info['Pieces Hash'] = self.get_file_pieces_hashes(file_data)

        return file_info

    def get_file_pieces_hashes(self, data):
        """
        Dividing the file to pieces and make on each piece a hash.
        """
        pieces_hashes = []

        for index in range(0, (len(data) / self.piece_length) + 1):
            if index == (len(data) / self.piece_length) + 1:
                pieces_hashes.append(YftfCreator.get_data_hash(data[index * self.piece_length:]))
            else:
                pieces_hashes.append(
                    YftfCreator.get_data_hash(data[index * self.piece_length:(index + 1) * self.piece_length]))

            self.num_pieces += 1

        return pieces_hashes

    @staticmethod
    def get_data_hash(data):
        """
        Make a SHA-1 hash on the data.
        """
        return hashlib.sha1(data).hexdigest()
