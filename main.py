import time
import threading

import WoeUSB.list_devices as list_devices
import WoeUSB.core as core


def on_install():
    global woe

    device = "/dev/sdb"

    iso = "/home/ketronix/Загрузки/elementaryos-6.1-stable.20211218-rc.iso"
        
    filesystem = "FAT"

    woe = WoeUSB_handler(iso, device, boot_flag=True, filesystem=filesystem)
    woe.start()

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

on_install()