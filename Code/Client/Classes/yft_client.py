import socket
import random
import string
import client_worker
import os
import json
import hashlib
import yftf_creator


class YFTClient(object):
    def __init__(self):
        self.peer_id = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
        self.peer_ip = YFTClient.get_host_ip()

        self.yftf_files = dict()
        self.workers = dict()

        self.thread_counter = 0
        self.start_port_from = 6000
        self.num_port_per_thread = 10

        self.downloads_dir_path = raw_input("Where do you want your downloads to be saved?")

        while True:
            command = raw_input("What do you want to do next?")

            if command == str(0):
                self.new_download()
                continue

            if command == str(1):
                self.new_share()
                continue

            if command == str(2):
                self.stop_upload()
                continue

    def new_download(self):
        yftf_path = raw_input("What is the yftf file path? ")

        if not os.path.isfile(yftf_path):
            print "Your yftf file doesn't exists"
            return

        yftf_file = open(yftf_path, 'r')
        yftf_data = yftf_file.read()
        yftf_json = json.loads(yftf_data)
        yftf_file.close()

        info_hash = hashlib.sha1(yftf_json["Info"]).hexdigest()

        self.yftf_files.update({info_hash: [yftf_json, self.downloads_dir_path]})

        worker = client_worker.ClientWorker(0, self.yftf_files, info_hash, self.peer_id, self.peer_ip, range(self.start_port_from + self.num_port_per_thread * self.thread_counter, self.num_port_per_thread), self.num_port_per_thread, self.num_port_per_thread * 10)

        self.workers.update({info_hash: worker})
        worker.start_client()

        self.thread_counter += 1

    def new_share(self):
        path = raw_input("Where the file/s you want to share is/are?")
        yftf_path = raw_input("Where do you want to save the yftf file? ")
        tracker_url = raw_input("What is your tracker server url?")

        yftf_creator.YftfCreator(path, yftf_path, tracker_url)

        yftf_file = open(os.path.join(yftf_path, path.split('\\')[-1].split('.')[0] + ".yftf"), 'r')
        yftf_data = yftf_file.read()
        yftf_json = json.loads(yftf_data)
        yftf_file.close()

        info_hash = hashlib.sha1(json.dumps(yftf_json["Info"])).hexdigest()

        self.yftf_files.update({info_hash: [yftf_json, self.downloads_dir_path]})

        worker = client_worker.ClientWorker(1, self.yftf_files, info_hash, self.peer_id, self.peer_ip, range(self.start_port_from, self.start_port_from + self.num_port_per_thread), self.num_port_per_thread, self.num_port_per_thread * 10)

        self.workers.update({info_hash: worker})
        worker.start_client()

        self.thread_counter += 1

    def stop_upload(self):
        shared_file_name = raw_input("What is the name of the shared file/s?")
        info_hash = ""

        for info_hash, data in self.yftf_files.iteritems():
            if data[0]["Info"]["Name"] is shared_file_name:
                del self.yftf_files[info_hash]
                break

        if len(info_hash) < 0:
            print "ERROR: You don't upload this files"
            return

        self.workers[info_hash].stop_upload()
        del self.workers[info_hash]

        self.thread_counter -= 1

    @staticmethod
    def get_host_ip():
            sock = socket.socket()
            sock.connect(("google.com", 80))
            ip = sock.getsockname()[0]
            sock.close()

            return ip


def main():
    YFTClient()


if __name__ == "__main__":
    main()
