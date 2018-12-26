import subprocess as s
import shlex as sh


path = "/Users/dtrenhaile/Desktop/"
top_dir = path + ""  # dataset
save_dir = path + ""  # save directory for analysis

s.call(sh.split("python main.py --directory " + top_dir + " --save " + save_dir))
