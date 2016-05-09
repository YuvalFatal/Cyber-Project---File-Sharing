import socket
import random
import string
import client_worker
import os
import json
import hashlib
import yftf_creator
import thread


class YFTClient(object):
    def __init__(self):
        self.peer_id = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
        self.peer_ip = YFTClient.get_host_ip()

        self.yftf_files = dict()

        self.thread_counter = 0
        self.start_port_from = 6000
        self.num_port_per_thread = 10

        self.downloads_dir_path = ""
        self.yftf_dir_path = ""
        self.yftf_path = ""
        self.shared_files_dir_path = ""
        self.tracker_url = ""
        self.command = -1

        self.worker_object = client_worker.ClientWorker(self.yftf_files, 1, 1)

        thread.start_new_thread(self.worker_object.start_client, ())

    def new_action(self):
        if self.command is -1:
            return

        if self.command is 0:
            self.new_download()
            return

        if self.command is 1:
            self.new_share()
            return

        if self.command is 2:
            self.stop_upload()
            return

    def correct_path(self):
        self.downloads_dir_path = self.downloads_dir_path.replace('/', '\\')
        self.yftf_dir_path = self.yftf_dir_path.replace('/', '\\')
        self.yftf_path = self.yftf_path.replace('/', '\\')
        self.shared_files_dir_path = self.shared_files_dir_path.replace('/', '\\')

    def new_download(self):
        self.correct_path()

        if not os.path.isfile(self.yftf_path):
            print "Error: Your yftf file doesn't exists"
            return

        yftf_file = open(self.yftf_path, 'r')
        yftf_data = yftf_file.read()
        yftf_json = json.loads(yftf_data)
        yftf_file.close()

        info_hash = hashlib.sha1(json.dumps(yftf_json["Info"])).hexdigest()

        self.yftf_files.update({info_hash: [yftf_json, self.downloads_dir_path]})

        self.worker_object.add_action(0, self.yftf_files, info_hash, self.peer_id, self.peer_ip, range(self.start_port_from + self.num_port_per_thread * self.thread_counter, self.num_port_per_thread), self.num_port_per_thread, self.num_port_per_thread * 10)

        self.thread_counter += 1

    def new_share(self):
        self.correct_path()

        yftf_creator.YftfCreator(self.shared_files_dir_path, self.yftf_dir_path, self.tracker_url)

        yftf_file = open(os.path.join(self.yftf_dir_path, self.shared_files_dir_path.split('\\')[-1].split('.')[0] + ".yftf"), 'r')
        yftf_data = yftf_file.read()
        yftf_json = json.loads(yftf_data)
        yftf_file.close()

        info_hash = hashlib.sha1(json.dumps(yftf_json["Info"])).hexdigest()

        self.yftf_files.update({info_hash: [yftf_json, self.downloads_dir_path]})

        self.worker_object.add_action(1, self.yftf_files, info_hash, self.peer_id, self.peer_ip, range(self.start_port_from, self.start_port_from + self.num_port_per_thread), self.num_port_per_thread, self.num_port_per_thread * 10)

        self.thread_counter += 1

    def stop_upload(self):
        self.correct_path()

        shared_file_name = self.yftf_path.split('\\')[-1].split('.')[0]
        info_hash = ""

        for info_hash, data in self.yftf_files.iteritems():
            if data[0]["Info"]["Name"] is shared_file_name:
                del self.yftf_files[info_hash]
                break

        if len(info_hash) < 0:
            print "ERROR: You don't upload this files"
            return

        self.worker_object.add_action(2, self.yftf_files, info_hash, self.peer_id, self.peer_ip, range(self.start_port_from, self.start_port_from + self.num_port_per_thread), 1, self.num_port_per_thread * 10)

        self.worker_object.stop_action(info_hash)

        self.thread_counter -= 1

    @staticmethod
    def get_host_ip():
            sock = socket.socket()
            sock.connect(("google.com", 80))
            ip = sock.getsockname()[0]
            sock.close()

            return ip
