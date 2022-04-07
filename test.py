import time
import os
import threading

from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog as fd

from click import progressbar

import WoeUSB.list_devices as list_devices
import WoeUSB.core as core


pulse_started = False

def on_install():
    if PathEntry.get() != "":
        global woe, pulse_started
        if messagebox.askquestion("Внимание!", "Уверены? Все данные на выбранном носителе будут УНИЧТОЖЕНЫ! Возможно, без возможности восстановления.") == "no":
            return

        device = DeviceWidget.get().split(" ")[0]

        iso = PathEntry.get()
        
        filesystem = "FAT"

        progress_bar.start()

        woe = WoeUSB_handler(iso, device, boot_flag=True, filesystem=filesystem)
        woe.start()

        while woe.is_alive():
            if not woe.progress:
                labelStatus['text'] = str(woe.state)
                # if pulse_started != True:
                #     progress_bar.start()
                #     pulse_started = True
                time.sleep(0.06)
            else:
                # if pulse_started != False:
                #     progress_bar.stop()
                #     progress_bar.configure(mode = "determinate")
                #     pulse_started = False
                labelStatus['text'] = str(woe.state)
                progress_bar['value'] = progress_bar['value'] + 1

            # if not status:
            #     if messagebox.askquestion("Внимание!", "Точно хотите отменить запись образа?", "Cancel") == "no":
            #         dialog.Resume()
            #     else:
            #         woe.kill = True
            #         break

        if woe.error == "":
            messagebox.showinfo("Внимание!","Запись завершена успешно!!")
        else:
            messagebox.showinfo("Внимание!", "Упс... Что-то сломалось. Записать образ не удалось!" + "\n" + str(woe.error))

def open_iso():
    file_name = fd.askopenfilename(filetypes = ((".ISO files", ".iso"), (".DMG files", ".dmg"), (".IMG files", ".img"), (".RAW files", ".raw")))
    if file_name != "":
        PathEntry.delete(0,"end")
        PathEntry.insert(0, file_name)
        print(PathEntry.get())


window = Tk()
window.title("Rufus")
window.geometry("350x200")
window.resizable(width=False, height=False)

devices = ["Choise the device"]
devices.extend(list_devices.usb_drive())

PathEntry = Entry(window)
PathEntry.place(x = 7, y = 5, width = 240)

buttonOpen = Button(window, text = "Открыть" ,command=open_iso)
buttonOpen.place(x = 250, y = 4, height = 30, width = 90)

DeviceWidget = ttk.Combobox(window, values = devices)
DeviceWidget.current(0)
DeviceWidget.place(x = 7, y = 50, width = 340)

buttonStart = Button(window, text = "Start" ,command=on_install)
buttonStart.place(x = 250, y = 160, height = 30, width = 90)

labelStatus = Label(window, text = "Status: Wait", anchor='w')
labelStatus.place(x = 0, y = 100, height = 20, width = 340)

progress_bar = ttk.Progressbar(window, orient="horizontal", mode="indeterminate", maximum=100, value=0)
progress_bar.place(x = 7, y = 130, width = 340)


class WoeUSB_handler(threading.Thread):
    """
    Class for handling communication with woeusb.
    """
    progress = False
    state = ""
    error = ""
    kill = False

    def __init__(self, source, target, boot_flag, filesystem):
        threading.Thread.__init__(self)

        core.gui = self
        self.source = source
        self.target = target
        self.boot_flag = boot_flag
        self.filesystem = filesystem

    def run(self):
        source_fs_mountpoint, target_fs_mountpoint, temp_directory, target_media = core.init(
            from_cli=False,
            install_mode="device",
            source_media=self.source,
            target_media=self.target
        )
        try:
            core.main(source_fs_mountpoint, target_fs_mountpoint, self.source, self.target, "device", temp_directory,
                      self.filesystem, self.boot_flag)
        except SystemExit:
            pass

        core.cleanup(source_fs_mountpoint, target_fs_mountpoint, temp_directory, target_media)


window.mainloop()