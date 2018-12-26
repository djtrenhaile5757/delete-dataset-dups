import subprocess as s
import shlex as sh


path = "/Users/dtrenhaile/Desktop/"
top_dir = path + "test"  # "dataset"
save_dir = path + "save"  # "dup_analysis"

s.call(sh.split("python main.py --directory " + top_dir + " --save " + save_dir))
