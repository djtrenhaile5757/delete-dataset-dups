import subprocess as s
import shlex as sh


path = #path_to_directories
top_dir = path + "test" 
save_dir = path + "save"

s.call(sh.split("python main.py --directory " + top_dir + " --save " + save_dir))
