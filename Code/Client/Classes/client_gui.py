"""
The GUI file.
Run this to start the client.
"""
from Tkinter import *
import tkFileDialog
import yft_client


class ClientGUI(Tk):
    """
    The main GUI class.
    """

    def __init__(self):
        """
        Starting the GUI.
        """

        Tk.__init__(self)

        yft_client_obj = yft_client.YFTClient()
        container = Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for page in (StartPage, NewDownloadPage, NewSharePage, StopUploadPage):
            frame = page(container, self, yft_client_obj)
            self.frames[page] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, page):
        """
        Show different frame.
        """
        frame = self.frames[page]
        frame.tkraise()


class StartPage(Frame):
    """
    The start page class.
    """

    def __init__(self, parent, controller, yft_client_obj):
        """
        Organize its frame.
        """
        Frame.__init__(self, parent)

        self.yft_client_obj = yft_client_obj

        change_downloads = Button(self)
        change_downloads["text"] = "Change Downloads Dir"
        change_downloads["command"] = self.choose_downloads_path

        self.download_path = Entry(self, textvariable=self.yft_client_obj.downloads_dir_path, width=80)
        self.download_path.config(state=DISABLED)

        change_yftf = Button(self)
        change_yftf["text"] = "Change yftf Dir"
        change_yftf["command"] = self.choose_yftf_path

        self.yftf_path = Entry(self, textvariable=self.yft_client_obj.downloads_dir_path, width=80)
        self.yftf_path.config(state=DISABLED)

        change_downloads.grid(row=0, column=0, padx=10, pady=10)

        self.download_path.grid(row=0, column=1, padx=10, pady=10)

        change_yftf.grid(row=1, column=0, padx=10, pady=10)

        self.yftf_path.grid(row=1, column=1, padx=10, pady=10)

        new_download_button = Button(self)
        new_download_button["text"] = "New Download"
        new_download_button["command"] = lambda: controller.show_frame(NewDownloadPage)

        new_share_button = Button(self)
        new_share_button["text"] = "New Share"
        new_share_button["command"] = lambda: controller.show_frame(NewSharePage)

        stop_update_button = Button(self)
        stop_update_button["text"] = "Stop Update/Download"
        stop_update_button["command"] = lambda: controller.show_frame(StopUploadPage)

        new_download_button.grid(row=2, column=0, padx=10, pady=10)
        new_share_button.grid(row=2, column=1, padx=10, pady=10)
        stop_update_button.grid(row=3, column=0, padx=10, pady=10)

    def choose_downloads_path(self):
        """
        Choose downloads path.
        """
        self.yft_client_obj.downloads_dir_path = tkFileDialog.askdirectory(
            parent=self, initialdir="/",
            title='Please select the directory you want your downloads to be saved')

        self.download_path.config(state=NORMAL)
        self.download_path.delete(0, END)
        self.download_path.insert(0, self.yft_client_obj.downloads_dir_path)
        self.download_path.config(state=DISABLED)

    def choose_yftf_path(self):
        """
        Choose yftf path.
        """
        self.yft_client_obj.yftf_dir_path = tkFileDialog.askdirectory(
            parent=self, initialdir="/",
            title='Please select the directory you want your yftf files to be saved')

        self.yftf_path.config(state=NORMAL)
        self.yftf_path.delete(0, END)
        self.yftf_path.insert(0, self.yft_client_obj.yftf_dir_path)
        self.yftf_path.config(state=DISABLED)


class NewDownloadPage(Frame):
    """
    New download frame class.
    """

    def __init__(self, parent, controller, yft_client_obj):
        """
        Organize the frame.
        """
        Frame.__init__(self, parent)

        self.yft_client_obj = yft_client_obj

        home_button = Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage))

        change_yftf = Button(self)
        change_yftf["text"] = "Change yftf Path"
        change_yftf["command"] = self.choose_yftf_path

        self.yftf_path = Entry(self, textvariable=self.yft_client_obj.yftf_path, width=80)
        self.yftf_path.config(state=DISABLED)

        download_button = Button(self)
        download_button["text"] = "Download"
        download_button["command"] = self.download

        home_button.grid(row=0, column=0, padx=10, pady=10)
        change_yftf.grid(row=1, column=0, padx=10, pady=10)
        self.yftf_path.grid(row=1, column=1, padx=10, pady=10)
        download_button.grid(row=2, column=0, padx=10, pady=10)

    def choose_yftf_path(self):
        """
        Choose yftf path.
        """
        self.yft_client_obj.yftf_path = tkFileDialog.askopenfilename(
            parent=self, initialdir="/",
            title='Please select the yftf file you want to download from')

        self.yftf_path.config(state=NORMAL)
        self.yftf_path.delete(0, END)
        self.yftf_path.insert(0, self.yft_client_obj.yftf_path)
        self.yftf_path.config(state=DISABLED)

    def download(self):
        """
        Start download.
        """
        self.yft_client_obj.command = 0
        self.yft_client_obj.new_action()


class NewSharePage(Frame):
    """
    New share frame class.
    """

    def __init__(self, parent, controller, yft_client_obj):
        """
        Organize the frame.
        """
        Frame.__init__(self, parent)

        self.yft_client_obj = yft_client_obj

        home_button = Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage))

        change_shared_files_dir_path = Button(self)
        change_shared_files_dir_path["text"] = "Change Shared Files Dir Path"
        change_shared_files_dir_path["command"] = self.choose_yftf_path

        self.shared_files_dir_path = Entry(self, textvariable=self.yft_client_obj.shared_files_dir_path, width=80)
        self.shared_files_dir_path.config(state=DISABLED)

        tracker_url_label = Label(self)
        tracker_url_label["text"] = "Tracker Url:"

        self.tracker_url = Entry(self, textvariable=self.yft_client_obj.tracker_url, width=80)

        share_button = Button(self)
        share_button["text"] = "Share"
        share_button["command"] = self.share

        home_button.grid(row=0, column=0, padx=10, pady=10)
        change_shared_files_dir_path.grid(row=1, column=0, padx=10, pady=10)
        self.shared_files_dir_path.grid(row=1, column=1, padx=10, pady=10)
        tracker_url_label.grid(row=2, column=0, padx=10, pady=10)
        self.tracker_url.grid(row=2, column=1, padx=10, pady=10)
        share_button.grid(row=3, column=0, padx=10, pady=10)

    def choose_yftf_path(self):
        """
        Choose yftf path.
        """
        self.yft_client_obj.shared_files_dir_path = tkFileDialog.askdirectory(
            parent=self, initialdir="/",
            title='Please select the directory which there are the files you want to share')

        self.shared_files_dir_path.config(state=NORMAL)
        self.shared_files_dir_path.delete(0, END)
        self.shared_files_dir_path.insert(0, self.yft_client_obj.shared_files_dir_path)
        self.shared_files_dir_path.config(state=DISABLED)

    def share(self):
        """
        Start sharing the new file.
        """
        self.yft_client_obj.command = 1
        self.yft_client_obj.tracker_url = self.tracker_url.get()
        self.yft_client_obj.new_action()


class StopUploadPage(Frame):
    """
    Stop upload/download frame.
    """

    def __init__(self, parent, controller, yft_client_obj):
        """
        Organize the frame.
        """
        Frame.__init__(self, parent)

        self.yft_client_obj = yft_client_obj

        home_button = Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage))

        change_yftf = Button(self)
        change_yftf["text"] = "Change yftf Path"
        change_yftf["command"] = self.choose_yftf_path

        self.yftf_path = Entry(self, textvariable=self.yft_client_obj.yftf_path, width=80)
        self.yftf_path.config(state=DISABLED)

        stop_button = Button(self)
        stop_button["text"] = "Stop"
        stop_button["command"] = self.stop

        home_button.grid(row=0, column=0, padx=10, pady=10)
        change_yftf.grid(row=1, column=0, padx=10, pady=10)
        self.yftf_path.grid(row=1, column=1, padx=10, pady=10)
        stop_button.grid(row=2, column=0, padx=10, pady=10)

    def choose_yftf_path(self):
        """
        Choose yftf path.
        """
        self.yft_client_obj.yftf_path = tkFileDialog.askopenfilename(
            parent=self, initialdir="/",
            title='Please select the yftf file you want to stop download/upload')

        self.yftf_path.config(state=NORMAL)
        self.yftf_path.delete(0, END)
        self.yftf_path.insert(0, self.yft_client_obj.yftf_path)
        self.yftf_path.config(state=DISABLED)

    def stop(self):
        """
        Stop upload/download.
        """
        self.yft_client_obj.command = 2
        self.yft_client_obj.new_action()


def main():
    """
    Starting the client.
    """
    app = ClientGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
