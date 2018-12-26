import argparse
import os
from dup_searcher import DuplicateSearcher

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", required=True, help="Top level directory")
ap.add_argument("-s", "--save", required=False, help="save location were possible duplicates are stored for review; \
                                                     if unprovided, duplicates will be automatically deleted")
ap.add_argument("-n", "--distance", default=0.01, help="maximum chi-squared distance \
                                                       allowed between query and relevant histograms")
args = vars(ap.parse_args())


# ##### initialize ######

# handle unclean directories
def clean_directories():
    print("[INFO] Cleaning directories...")

    save_dirs = ()
    save_files = ()
    # gather directory info and delete hidden .DS_Store files
    for dirpath, dirnames, files in os.walk(args["save"]):
        save_dirs = dirnames
        save_files = files
        for file in files:
            if file == ".DS_Store":
                os.remove(os.path.join(dirpath, file))
                print("[INFO] Deleting .DS_Store file in save directory...")
        for dir in dirnames:
            for sub_dirpath, _, sub_files in os.walk(dir):
                for sub_file in sub_files:
                    if sub_file == ".DS_Store":
                        os.remove(os.path.join(sub_dirpath, sub_file))
                        print("[INFO] Deleting .DS_Store file in save directory...")

    for dirpath, dirnames, files in os.walk(args["directory"]):
        for file in files:
            if file == ".DS_Store":
                os.remove(os.path.join(dirpath, file))
                print("[INFO] Deleting .DS_Store file in top directory...")
        for dir in dirnames:
            for sub_dirpath, _, sub_files in os.walk(dir):
                for sub_file in sub_files:
                    if sub_file == ".DS_Store":
                        os.remove(os.path.join(sub_dirpath, sub_file))
                        print("[INFO] Deleting .DS_Store file in top directory...")
    print()

    # check that the directory is empty
    if len(save_dirs) > 0 or len(save_files) > 0:
        print("[INFO] Designated save directory is not empty.")
        print("     This could interfere with the saving of duplicates. Please")
        print("     clear the directory or terminate and designate another")
        print("     before proceeding.")
        print()

        print(args["save"])
        print("contains: ")
        for _, dirnames, files in os.walk(args["save"]):
            for file in files:
                print("     " + file)
            for dir in dirnames:
                print()
                print("     subdir: " + dir)
                for _, _, files in os.walk(dir):
                    for file in files:
                        print("     " + file)

        try:
            input("Continue? [enter]")
        except SyntaxError:
            pass


clean_directories()
searcher = DuplicateSearcher(args["directory"], args["save"], args["distance"])

auto_del = False
if not isinstance(args["save"], str):
    auto_del = True

# start processing
print("[INFO] Beginning histogram image comparison...")
print("     Auto-Delete: " + str(auto_del))
print()
if not auto_del:
    duplicates, empty, num_dups = searcher.gather_duplicates("save")

    print()
    print()
    print("[INFO] Comparisons complete; ready to delete duplicates.")
    print("[INFO] Please review the selected images in your given save directory.")
    print("     Delete an image from duplicates subdirectory to prevent it from being purged")
    print("     from the original dataset.")
    print()
    print("Total Duplicates: " + str(num_dups))
    print()

    try:
        input("Continue? [enter]")
    except SyntaxError:
        pass

    if not empty:
        searcher.gather_duplicates("save", duplicates)
else:
    searcher.gather_duplicates("delete")

print("[INFO] Terminating histogram comparison...")
