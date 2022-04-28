#! /usr/bin/env python3

import threading
from argparse import ArgumentParser
import WoeUSB.core as core

def standalone_installer(device:str, iso:str, filesystem:str):
    global woe

    workerThread = WoeUSB_handler(iso, device, boot_flag=True, filesystem=filesystem)
    workerThread.start()

    # Wait for the thread to complete
    workerThread.join()

class WoeUSB_handler(threading.Thread):
    """
    Class for handling communication with woeusb.
    """

    progress:bool = False
    state:str = ""
    error:str = ""
    kill:bool = False

    def __init__(self, source, target, boot_flag, filesystem):
        """
        Keyword arguments:
        - source -- Source image .iso or .img file.
        - target -- Device which will be flashed with the image. Example: /dev/sdb
        - boot_flag = Whether the flashed device should have boot flag
        """

        # Initialize the thread
        threading.Thread.__init__(self)

        core.gui = self
        self.source = source
        self.target = target
        self.boot_flag = boot_flag
        self.filesystem = filesystem

    def run(self):
        source_fs_mountpoint, target_fs_mountpoint, _ = core.init(
            from_cli=False,
            install_mode="device",
            source_media=self.source,
            target_media=self.target
        )

        core.main(source_fs_mountpoint, target_fs_mountpoint, self.source, self.target, "device",
                      self.filesystem, self.boot_flag)
        core.cleanup("/media/woeusb_source", "/media/woeusb_target", parsed_args.destination)


if __name__ == '__main__':
    args = ArgumentParser(description="Rufus for linux. Allows you to flash USB drives using CLI/GUI.")

    args.add_argument("source", type=str, help="Location of file, which will be flashed to the USB drive")
    args.add_argument("destination", type=str, help="Device (e.x. /dev/sdb) which will be flashed with the image. Note that all data on the device will be destroyed")

    args.add_argument("--filesystem", type=str, default="vfat", required=False, help="Filesystem type, used to format the drive")

    # Parse the arguments from sys.argv
    parsed_args = args.parse_args()

    print(parsed_args.source)
    print(parsed_args.destination)
    print(parsed_args.filesystem)

    # run the installer with provided arguments
    standalone_installer(device=parsed_args.destination, iso=parsed_args.source, filesystem=parsed_args.filesystem)