import getpass
import os


username = getpass.getuser()
os.system("ls /media/"+str(username)+"/FLASH")
print(username)