import os


output_stream = os.popen('pkexec cp -rv /home/ketronix/archlinux-2022.03.01-x86_64/* /home/ketronix/test')
out = output_stream.read().split('\n')
print("out: "+out[0])