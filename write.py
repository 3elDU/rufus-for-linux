import os
import sys


def formate_usb(device:str, file_system:str, name:str):
    print("unmountig device")
    os.system("umount -Rf "+device)
    print("Wipe device")
    os.system("mkfs."+file_system+" -I -n "+name+" "+device)

def write_iso(iso_file:str, device_to_write:str):
    os.system("umount -f "+iso_file)
    formate_usb(device=device_to_write, file_system="vfat", name="FLASH")
    print("mounting iso...")
    os.system("mkdir /mnt/iso")
    os.system("mkdir /mnt/flash")
    os.system("mount -o loop "+iso_file+" /mnt/iso")
    print("mount device")
    os.system("mount "+device_to_write+" /mnt/flash")
    print("writing...")
    os.system("cp -rLv /mnt/iso/* /mnt/flash")
    print("DONE!!!")
    os.system("umount -Rf "+device_to_write)
    os.system("umount -f "+iso_file)


write_iso(iso_file=sys.argv[1], device_to_write=sys.argv[2])