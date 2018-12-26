import subprocess as s
import shlex as sh


path = "/Users/dtrenhaile/Desktop/"
top_dir = path + "test"# "1995_white_Chevy_Sonic_copy"
save_dir = path + "save"

s.call(sh.split("python main.py --directory " + top_dir + " --save " + save_dir))
