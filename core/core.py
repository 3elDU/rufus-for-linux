#!/usr/bin/env python3

import os
import time
import shutil
import threading
import subprocess
import urllib.request
import workaround
import utils

#: Increase verboseness, provide more information when required
verbose = False

debug = False

#: used in cleanup()
target_device = ""

application_name = "Rufus-for-Linux"

CopyFiles_handle = threading.Thread()

#: Execution state for cleanup functions to determine if clean up is required
current_state = 'pre-init'

gui = None


def main(source_fs_mountpoint, target_fs_mountpoint, source_media, target_media, install_mode, temp_directory,
         target_filesystem_type, workaround_bios_boot_flag, parser=None):
    """
    :param parser:
    :param source_fs_mountpoint:
    :param target_fs_mountpoint:
    :param source_media:
    :param target_media:
    :param install_mode:
    :param temp_directory:
    :param target_filesystem_type:
    :param workaround_bios_boot_flag:
    :return: 0 - succes; 1 - failure
    """
    global debug
    global verbose
    global no_color
    global current_state
    global target_device

    current_state = 'enter-init'

    command_mkdosfs, command_mkntfs, command_grubinstall = utils.check_runtime_dependencies(application_name)
    if command_grubinstall == "grub-install":
        name_grub_prefix = "grub"
    else:
        name_grub_prefix = "grub2"


    if os.getuid() != 0:
        utils.print_with_color("Warning: You are not running " + application_name + " as root!", "yellow")
        utils.print_with_color("Warning: This might be the reason of the following failure.", "yellow")

    if utils.check_runtime_parameters(install_mode, source_media, target_media):
        parser.print_help()
        return 1

    target_device, target_partition = utils.determine_target_parameters(install_mode, target_media)

    if utils.check_source_and_target_not_busy(install_mode, source_media, target_device, target_partition):
        return 1

    current_state = "start-mounting"

    if mount_source_filesystem(source_media, source_fs_mountpoint):
        utils.print_with_color("Error: Unable to mount source filesystem", "red")
        return 1

    if target_filesystem_type == "FAT":
        if utils.check_fat32_filesize_limitation(source_fs_mountpoint):
            target_filesystem_type = "NTFS"

    if install_mode == "device":
        wipe_existing_partition_table_and_filesystem_signatures(target_device)
        create_target_partition_table(target_device, "legacy")
        create_target_partition(target_device, target_partition, target_filesystem_type, target_filesystem_type,
                                command_mkdosfs,
                                command_mkntfs)

        if target_filesystem_type == "NTFS":
            create_uefi_ntfs_support_partition(target_device)
            install_uefi_ntfs_support_partition(target_device + "2", temp_directory)

    if install_mode == "partition":
        utils.check_target_partition(target_partition, target_device)
        utils.check_target_partition(target_partition, target_device)

    if mount_target_filesystem(target_partition, target_fs_mountpoint):
        utils.print_with_color("Error: Unable to mount target filesystem", "red")
        return 1

    if utils.check_target_filesystem_free_space(target_fs_mountpoint, source_fs_mountpoint, target_partition):
        return 1

    current_state = "copying-filesystem"

    workaround.linux_make_writeback_buffering_not_suck(True)

    copy_filesystem_files(source_fs_mountpoint, target_fs_mountpoint)

    workaround.support_windows_7_uefi_boot(source_fs_mountpoint, target_fs_mountpoint)

    install_legacy_pc_bootloader_grub(target_fs_mountpoint, target_device, command_grubinstall)

    install_legacy_pc_bootloader_grub_config(target_fs_mountpoint, target_device, command_grubinstall, name_grub_prefix)

    if workaround_bios_boot_flag:
        workaround.buggy_motherboards_that_ignore_disks_without_boot_flag_toggled(target_device)

    current_state = "finished"

    return 0



def wipe_existing_partition_table_and_filesystem_signatures(target_device):
    """
    :param target_device:
    :return: None
    """
    utils.print_with_color("Wiping all existing partition table and filesystem signatures in " + target_device, "green")
    subprocess.run(["wipefs", "--all", target_device])
    check_if_the_drive_is_really_wiped(target_device)


def check_if_the_drive_is_really_wiped(target_device):
    """
    Some broken locked-down flash drive will appears to be successfully wiped but actually nothing is written into it and will shown previous partition scheme afterwards.  This is the detection of the case and will bail out if such things happened

    :param target_device: The target device file to be checked
    :return: 0 - success; 1 - failure
    """
    utils.check_kill_signal()

    utils.print_with_color("Ensure that " + target_device + " is really wiped...")

    lsblk = subprocess.run(["lsblk", "--pairs", "--output", "NAME,TYPE", target_device], stdout=subprocess.PIPE).stdout

    grep = subprocess.Popen(["grep", "--count", "TYPE=\"part\""], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    if grep.communicate(input=lsblk)[0].decode("utf-8").strip() != "0":
        utils.print_with_color(
            "Error: Partition is still detected after wiping all signatures, this indicates that the drive might be locked into readonly mode due to end of lifespan.")
        return 1
    return 0


def create_target_partition_table(target_device, partition_table_type):
    """
    :param target_device:
    :param partition_table_type:
    :return: 0 - success; 1 - failure
    """
    utils.check_kill_signal()

    utils.print_with_color("Creating new partition table on " + target_device + "...", "green")

    if partition_table_type in ["legacy", "msdos", "mbr", "pc"]:
        parted_partiton_table_argument = "msdos"
    elif partition_table_type in ["gpt", "guid"]:
        utils.print_with_color("Error: Currently GUID partition table is not supported.", "red")
        return 1
    else:
        utils.print_with_color("Error: Partition table not supported.", "red")
        return 1

    # Create partition table(and overwrite the old one, whatever it was)
    subprocess.run(["parted", "--script", target_device, "mklabel", parted_partiton_table_argument])

    return 0


def create_target_partition(target_device, target_partition, filesystem_type, filesystem_label, command_mkdosfs,
                            command_mkntfs):
    """
    :param target_device:
    :param target_partition:
    :param filesystem_type:
    :param filesystem_label:
    :param command_mkdosfs:
    :param command_mkntfs:
    :return: 1,2 - failure
    """
    utils.check_kill_signal()

    if filesystem_type in ["FAT", "vfat"]:
        parted_mkpart_fs_type = "fat32"
    elif filesystem_type in ["NTFS", "ntfs"]:
        parted_mkpart_fs_type = "ntfs"
    else:
        utils.print_with_color("Error: Filesystem not supported", "red")
        return 2

    utils.print_with_color("Creating target partition...", "green")

    # Create target partition
    # We start at 4MiB for grub (it needs a post-mbr gap for its code)
    # and alignment of flash memory block erase segment in general, for details see
    # http://www.gnu.org/software/grub/manual/grub.html#BIOS-installation and http://lwn.net/Articles/428584/
    # If NTFS filesystem is used we leave a 512KiB partition
    # at the end for installing UEFI:NTFS partition for NTFS support
    if parted_mkpart_fs_type == "fat32":
        subprocess.run(["parted",
                        "--script",
                        target_device,
                        "mkpart",
                        "primary",
                        parted_mkpart_fs_type,
                        "4MiB",
                        "100%"])  # last sector of the disk
    elif parted_mkpart_fs_type == "ntfs":
        # Major partition for storing user files
        # NOTE: Microsoft Windows has a bug that only recognize the first partition for removable storage devices, that's why this partition should always be the first one
        subprocess.run(["parted",
                        "--script",
                        target_device,
                        "mkpart",
                        "primary",
                        parted_mkpart_fs_type,
                        "4MiB",
                        "--",
                        "-1025s"])  # Leave 512KiB==1024sector in traditional 512bytes/sector disk, disks with sector with more than 512bytes only result in partition size greater than 512KiB and is intentionally let-it-be.
    # FIXME: Leave exact 512KiB in all circumstances is better, but the algorithm to do so is quite brainkilling.
    else:
        utils.print_with_color("FATAL: Illegal parted_mkpart_fs_type, please report bug.", "green")

    utils.check_kill_signal()

    workaround.make_system_realize_partition_table_changed(target_device)

    # Format target partition's filesystem
    if filesystem_type in ["FAT", "vfat"]:
        subprocess.run([command_mkdosfs, "-F", "32", target_partition])
    elif filesystem_type in ["NTFS", "ntfs"]:
        subprocess.run([command_mkntfs, "--quick", "--label", filesystem_label, target_partition])
    else:
        utils.print_with_color("FATAL: Shouldn't be here")
        return 1


def create_uefi_ntfs_support_partition(target_device):
    """
    :param target_device:
    :return: None
    """
    utils.check_kill_signal()

    # FIXME: The partition type should be `fat12` but `fat12` isn't recognized by Parted...
    # NOTE: The --align is set to none because this partition is indeed misaligned, but ignored due to it's small size

    subprocess.run(["parted",
                    "--align", "none",
                    "--script",
                    target_device,
                    "mkpart",
                    "primary",
                    "fat16",
                    "--", "-1024s", "-1s"])


def install_uefi_ntfs_support_partition(uefi_ntfs_partition, download_directory):
    """
    Install UEFI:NTFS partition by writing the partition image into the created partition

    FIXME: Currently this requires internet access to download the image from GitHub directly, it should be replaced by including the image in our datadir

    :param uefi_ntfs_partition: The previously allocated partition for installing UEFI:NTFS, requires at least 512KiB
    :param download_directory: The temporary directory for downloading UEFI:NTFS image from GitHub
    :return: 1 - failure
    """
    utils.check_kill_signal()

    try:
        file = urllib.request.urlretrieve("https://github.com/pbatard/rufus/raw/master/res/uefi/", "uefi-ntfs.img")[0]
    except urllib.request.ContentTooShortError:
        utils.print_with_color(
            "Warning: Unable to download UEFI:NTFS partition image from GitHub, installation skipped.  Target device might not be bootable if the UEFI firmware doesn't support NTFS filesystem.")
        return 1

    shutil.move(file, download_directory + "/" + file)  # move file to download_directory

    shutil.copy2(download_directory + "/uefi-ntfs.img", uefi_ntfs_partition)


def mount_source_filesystem(source_media, source_fs_mountpoint):
    """
    :param source_media:
    :param source_fs_mountpoint:
    :return: 1 - failure
    """
    utils.check_kill_signal()

    utils.print_with_color("Mounting source filesystem...", "green")

    # os.makedirs(source_fs_mountpoint, exist_ok=True)

    if subprocess.run(["mkdir", "--parents", source_fs_mountpoint]).returncode != 0:
        utils.print_with_color("Error: Unable to create " + source_fs_mountpoint + " mountpoint directory", "red")
        return 1

    if os.path.isfile(source_media):
        if subprocess.run(["mount",
                           "--options", "loop,ro",
                           "--types", "udf,iso9660",
                           source_media,
                           source_fs_mountpoint]).returncode != 0:
            utils.print_with_color("Error: Unable to mount source media", "red")
            return 1
    else:
        if subprocess.run(["mount",
                           "--options", "ro",
                           source_media,
                           source_fs_mountpoint]).returncode != 0:
            utils.print_with_color("Error: Unable to mount source media", "red")
            return 1


def mount_target_filesystem(target_partition, target_fs_mountpoint):
    """
    Mount target filesystem to existing path as mountpoint

    :param target_partition: The partition device file target filesystem resides, for example /dev/sdX1
    :param target_fs_mountpoint: The existing directory used as the target filesystem's mountpoint, for example /mnt/target_filesystem
    :return: 1 - failure
    """
    utils.check_kill_signal()

    utils.print_with_color("Mounting target filesystem...", "green")

    # os.makedirs(target_fs_mountpoint, exist_ok=True)

    if subprocess.run(["mkdir", "--parents", target_fs_mountpoint]).returncode != 0:
        utils.print_with_color("Error: Unable to create " + target_fs_mountpoint + " mountpoint directory", "red")
        return 1

    if subprocess.run(["mount",
                       target_partition,
                       target_fs_mountpoint]).returncode != 0:
        utils.print_with_color("Error: Unable to mount target media", "red")
        return 1


def copy_filesystem_files(source_fs_mountpoint, target_fs_mountpoint):
    """
    Copying all files from one filesystem to another, with progress reporting

    :param source_fs_mountpoint:
    :param target_fs_mountpoint:
    :return: None
    """
    global CopyFiles_handle

    utils.check_kill_signal()

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(source_fs_mountpoint):
        for file in filenames:
            path = os.path.join(dirpath, file)
            total_size += os.path.getsize(path)

    utils.print_with_color("Copying files from source media...", "green")

    CopyFiles_handle = ReportCopyProgress(source_fs_mountpoint, target_fs_mountpoint)
    CopyFiles_handle.start()

    for dirpath, _, filenames in os.walk(source_fs_mountpoint):
        utils.check_kill_signal()

        if not os.path.isdir(target_fs_mountpoint + dirpath.replace(source_fs_mountpoint, "")):
            os.mkdir(target_fs_mountpoint + dirpath.replace(source_fs_mountpoint, ""))
        for file in filenames:
            path = os.path.join(dirpath, file)
            CopyFiles_handle.file = path

            if os.path.getsize(path) > 5 * 1024 * 1024:  # Files bigger than 5 MiB
                copy_large_file(path, target_fs_mountpoint + path.replace(source_fs_mountpoint, ""))
            else:
                shutil.copy2(path, target_fs_mountpoint + path.replace(source_fs_mountpoint, ""))

    CopyFiles_handle.stop = True


def copy_large_file(source, target):
    """
    Because python's copy is atomic it is not possible to do anything during process.
    It is not a big problem when using cli (user can just hit ctrl+c and throw exception),
    but when using gui this part of script needs to "ping" gui for progress reporting
    and check if user didn't click "cancel" (see utils.check_kill_signal())

    :param source:
    :param target:
    :return: None
    """
    source_file = open(source, "rb")  # Open for reading in byte mode
    target_file = open(target, "wb")  # Open for writing in byte mode

    while True:
        utils.check_kill_signal()

        data = source_file.read(5 * 1024 * 1024)  # Read 5 MiB, speeds of shitty pendrives can be as low as 2 MiB/s
        if data == b"":
            break

        target_file.write(data)

    source_file.close()
    target_file.close()


def install_legacy_pc_bootloader_grub(target_fs_mountpoint, target_device, command_grubinstall):
    """
    :param target_fs_mountpoint:
    :param target_device:
    :param command_grubinstall:
    :return: None
    """
    utils.check_kill_signal()

    utils.print_with_color("Installing GRUB bootloader for legacy PC booting support...", "green")

    subprocess.run([command_grubinstall,
                    "--target=i386-pc",
                    "--boot-directory=" + target_fs_mountpoint,
                    "--force", target_device])


def install_legacy_pc_bootloader_grub_config(target_fs_mountpoint, target_device, command_grubinstall,
                                             name_grub_prefix):
    """
    Install a GRUB config file to chainload Microsoft Windows's bootloader in Legacy PC bootmode

    :param target_fs_mountpoint: Target filesystem's mountpoint(where GRUB is installed)
    :param target_device:
    :param command_grubinstall:
    :param name_grub_prefix: May be different between distributions, so need to be specified (grub/grub2)
    :return: None
    """
    utils.check_kill_signal()

    utils.print_with_color("Installing custom GRUB config for legacy PC booting...", "green")

    grub_cfg = target_fs_mountpoint + "/" + name_grub_prefix + "/grub.cfg"

    os.makedirs(target_fs_mountpoint + "/" + name_grub_prefix, exist_ok=True)

    with open(grub_cfg, "w") as cfg:
        cfg.write("ntldr /bootmgr\n")
        cfg.write("boot")


def cleanup_mountpoint(fs_mountpoint):
    """
    Unmount mounted filesystems and clean-up mountpoints before exiting program

    :param fs_mountpoint:
    :return: unclean(2): Not fully clean, target device can be safely detach from host; unsafe(3): Target device cannot be safely detach from host
    """
    if os.path.ismount(fs_mountpoint):  # os.path.ismount() checks if path is a mount point
        utils.print_with_color("Unmounting and removing " + fs_mountpoint + "...", "green")
        if subprocess.run(["umount", fs_mountpoint]).returncode:
            utils.print_with_color("Warning: Unable to unmount filesystem.", "yellow")
            return 1

        try:
            os.rmdir(fs_mountpoint)
        except OSError:
            utils.print_with_color("Warning: Unable to remove source mountpoint", "yellow")
            return 2

    return 0


def cleanup(source_fs_mountpoint, target_fs_mountpoint, temp_directory):
    """
    :param source_fs_mountpoint:
    :param target_fs_mountpoint:
    :param temp_directory:
    :return: None
    """
    if CopyFiles_handle.is_alive():
        CopyFiles_handle.stop = True

    if current_state in ["copying-filesystem", "finished"]:
        workaround.linux_make_writeback_buffering_not_suck(False)

    flag_unclean = False
    flag_unsafe = False

    cleanup_result = cleanup_mountpoint(source_fs_mountpoint)

    if cleanup_result == 2:
        flag_unclean = True

    cleanup_result = cleanup_mountpoint(target_fs_mountpoint)

    if cleanup_result == 1:
        flag_unsafe = True
    elif cleanup_result == 2:
        flag_unclean = True

    if flag_unclean:
        utils.print_with_color("Some mountpoints are not unmount/cleaned successfully and must be done manually",
                               "yellow")

    if flag_unsafe:
        utils.print_with_color(
            "We unable to unmount target filesystem for you, please make sure target filesystem is unmounted before detaching to prevent data corruption",
            "yellow")
        utils.print_with_color("Some mountpoints are not unmount/cleaned successfully and must be done manually",
                               "yellow")

    if utils.check_is_target_device_busy(target_device):
        utils.print_with_color(
            "Target device is busy, please make sure you unmount all filesystems on target device or shutdown the computer before detaching it.",
            "yellow")
    else:
        utils.print_with_color("You may now safely detach the target device", "green")

    shutil.rmtree(temp_directory)

    if current_state == "finished":
        utils.print_with_color("Done :)", "green")
        utils.print_with_color("The target device should be bootable now", "green")



class ReportCopyProgress(threading.Thread):
    """
    Classes for threading module
    """
    file = ""
    stop = False

    def __init__(self, source, target):
        threading.Thread.__init__(self)
        self.source = source
        self.target = target

    def run(self):
        source_size = utils.get_size(self.source)
        len_ = 0
        file_old = None

        while not self.stop:
            target_size = utils.get_size(self.target)

            if len_ != 0 and gui is None:
                print('\033[3A')
                print(" " * len_)
                print(" " * 4)
                print('\033[3A')

            # Prevent printing same filenames
            if self.file != file_old:
                file_old = self.file
                utils.print_with_color(self.file.replace(self.source, ""))

            string = "Copied " + utils.convert_to_human_readable_format(
                target_size) + " from a total of " + utils.convert_to_human_readable_format(source_size)

            len_ = len(string)
            percentage = (target_size * 100) // source_size

            if gui is not None:
                gui.state = string
                gui.progress = percentage
            else:
                print(string)
                print(str(percentage) + "%")

            time.sleep(0.05)
        if gui is not None:
            gui.progress = False

        return 0

