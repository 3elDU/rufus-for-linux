import os
import sys
from glob import iglob
from subprocess import Popen, PIPE
import time
import signal
from decimal import Decimal, localcontext, ROUND_DOWN


delim = " - "
endOption = "x" + delim + "Exit program"
optionString = "Enter Your Option : "
sureString = "Are you sure (Y/n) : "
invalidString = "Invalid option entered, Please Enter a valid option\n"
DEVICE = "/dev/sdb"
yes = ['YES', 'y', 'Y', 'yes', '']


def main():
    clearScreen()
    if len(sys.argv) > 1:
        createBootable(sys.argv[1], getUsb())
    else:
        createBootable(getFile(), getUsb())


def getFile():
    isoList = getIsos()
    printList(isoList)
    complete = False
    while not complete:
        optionList = list(range(1, len(isoList)+1))
        optionList.append('x')
        option = readOption(optionList)
        clearScreen()
        File = isoList[int(option)-1]
        return File
        complete = True


def readOption(myList):
    print()
    option = input(optionString)
    if option == 'x':
        quit()
    if (not option.isdigit() and option not in myList) or (
            option.isdigit() and int(option) not in myList):
        return readOption(myList)
    if input(sureString) in yes:
        return option
    quit()


def printList(isoList):
    count = 0
    for iso in isoList:
        count += 1
        print(str(count) + delim + os.path.basename(iso))
    print()
    print(endOption)


def getIsos():
    isoList = []
    count = 1
    for filename in iglob("**/*.iso", recursive=True):
        isoList.append(filename)
        count += 1
    return isoList


def createBootable(fileName, device):
        print("Format Device")
        os.system('umount '+device)
        os.system('mkfs.fat -I '+device)
        fileSize = getSize(fileName)
        dd = Popen(['dd'] + ['if='+fileName, 'of='+device],
                   stderr=PIPE, stdout=PIPE)
        os.system('clear')
        while dd.poll() is None:
            time.sleep(.3)
            dd.send_signal(signal.SIGUSR1)
            while 1:
                l = dd.stderr.readline()
                if b'bytes' in l:
                    done = int(l[:l.index(b'bytes')-1])
                    if(fileSize != 0):
                        progress = done/fileSize
                        progress = truncFloat(progress)
                        copyText = "Copying Files " + str(progress*100) + "%"
                        if(progress == 1):
                            copyText = "Completed Install, " + \
                                        "You may remove the usb device now\n"
                        updateProgress(progress, copyText)
                    break


def updateProgress(progress, copyText):
    print("\r"+copyText, end="", flush=True)


def truncFloat(floatNumber):
    with localcontext() as context:
        context.rounding = ROUND_DOWN
        return Decimal(floatNumber).quantize(Decimal('0.01'))


def getSize(fileName):
    file = open(fileName, 'rb')
    file.seek(0, 2)
    size = file.tell()
    return int(size)


def clearScreen():
    os.system('clear')


def getUsb():
    clearScreen()
    usbList = []
    usbRaw = os.popen('lsblk | grep -v sda').read()
    count = 1
    print("Select your device from the following list \n")
    print("    "+usbRaw.splitlines()[0])
    for line in usbRaw.splitlines()[1:]:
        usbList.append(line)
        print(str(count)+delim+line)
        count += 1
    print()
    print(endOption)
    option = readOption(list(range(1, len(usbList)+1)))
    if(option != 'x'):
        line = usbList[int(option)-1]
        device = line.split(" ", 1)[0]
        if("─" in device):
            device = device.split("─", 1)[1]
        return('/dev/'+device)
    return 'null'

if __name__ == "__main__":
    main()