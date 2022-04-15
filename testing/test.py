import tkinter,urllib.request, threading
from tkinter import ttk
import time
#
tm = time.time()
def call_passive():
    urllib.request.urlretrieve('https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-11.3.0-amd64-netinst.iso','debian-11.3.0-amd64-netinst.iso')
    print ('Done')
    return True
    
def call_active():
    pb.pack()
    pb.start() 
   
    if time.time() - tm < 1:
        root.after(1000, call_active)
        
th = threading.Thread(target = call_passive)
def starter(event):
    th.start()
    call_active()
root= tkinter.Tk()
pb = ttk.Progressbar(length = 200, orient = 'horizontal', mode = 'indeterminate')
but = tkinter.Button(root, text = 'Go!')
root.minsize(width = 400, height = 350)
but.bind('<Button-1>', starter)
but.pack()
root.mainloop()