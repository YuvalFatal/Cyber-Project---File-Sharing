import socket
import random
import string


class YFTClient(object):
    def __init__(self):
        self.peer_id = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(20))
        self.peer_ip = YFTClient.get_host_ip()

        self.yftf_files = dict()

        self.thread_counter = 0
        self.start_port_from = 6000
        self.num_port_per_thread = 10

        self.downloads_dir_path = raw_input("Where do you want your downloads to be saved?")

        while True:
            command = raw_input("What do you want to do next?")

            if command is str(0):
                self.new_download()
                continue

            if command is str(1):
                self.new_share()
                continue

            if command is str(2):
                self.stop_upload()
                continue

    def new_download(self):
        pass

    def new_share(self):
        pass

    def stop_upload(self):
        pass

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
