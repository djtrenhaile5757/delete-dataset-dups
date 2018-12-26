import subprocess as s
import shlex as sh


path = #path_to_directories
top_dir = path + "" #path_to_dataset 
save_dir = path + "" #path_to_save_directory

s.call(sh.split("python main.py --directory " + top_dir + " --save " + save_dir))
