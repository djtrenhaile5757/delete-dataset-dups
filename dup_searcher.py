import os
import cv2

from cbir.hsvdescriptor import HSVDescriptor
from cbir import dists


class DuplicateSearcher:
    def __init__(self, top, save, distance):
        self.top_dir = top
        self.save_dir = save
        self.desc = HSVDescriptor((4, 6, 3))
        self.distance = distance

    def gather_duplicates(self, action, duplicates="", i=1):
        if duplicates is not "":
            i = 1
            for dup in duplicates:
                self.delete_duplicate(dup, i)
                i += 1
        else:
            duplicates = list()
            errors = list()
            for query_top, query_subdirs, _ in os.walk(self.top_dir):
                for q_subdir in query_subdirs:
                    q_path = os.path.join(query_top, q_subdir)
                    for _, _, q_images in os.walk(q_path):
                        for query in q_images:
                            # get query image from a subdirectory of the top level
                            print("     query: " + query)
                            is_error = False
                            for error in errors:
                                if query == error:
                                    is_error = True

                            print("     error: " + str(is_error))
                            if not is_error:
                                print("[INFO] Query #" + str(i).zfill(7) + ": " + query)
                                i += 1

                                q = os.path.join(q_path, query)
                                q_im = cv2.imread(q)

                                q_features = ()
                                try:
                                    q_features = self.desc.describe(q_im)
                                except cv2.error as e:
                                    print(e)
                                    print("[INFO] Error on query image: " + q_subdir + "/" + query)
                                    print("     adding to error photos in save directory")

                                    path = os.path.join(query_top, q_subdir)
                                    self.save_error(q_im, query, path)
                                    errors.append(query)
                                    is_error = True

                                if not is_error:
                                    dup_query = False
                                    for dup in duplicates:
                                        q_array = [query, q_subdir]
                                        if q_array == dup:
                                            # the image has already been identified as a duplicate of another
                                            # and can therefore be safely ignored
                                            dup_query = True

                                    if not dup_query:
                                        for relevant_top, relevant_subdirs, _ in os.walk(self.top_dir):
                                            for r_subdir in relevant_subdirs:
                                                r_path = os.path.join(relevant_top, r_subdir)
                                                for _, _, r_images in os.walk(r_path):
                                                    for relevant in r_images:
                                                        # get a new comparison image
                                                        #
                                                        # print("     relevant: " + r_subdir + "/" + relevant)

                                                        for error in errors:
                                                            if relevant == error:
                                                                is_error = True
                                                                print("skipping " + relevant)

                                                        if not is_error:
                                                            r = os.path.join(r_path, relevant)

                                                            # asserts that relevant is not an iteration of the query
                                                            if not q == r:
                                                                r_im = cv2.imread(r)

                                                                r_features = ()
                                                                try:
                                                                    r_features = self.desc.describe(r_im)
                                                                except cv2.error as e:
                                                                    print(e)
                                                                    print("[INFO] Error on relevant image: " + r_subdir + "/" + relevant)
                                                                    print("     adding to error photos in save directory")
                                                                    is_error = True

                                                                    path = os.path.join(relevant_top, r_subdir)
                                                                    self.save_error(r_im, relevant, path)
                                                                    errors.append(relevant)

                                                                if not is_error:
                                                                    d = dists.chi2_distance(r_features, q_features)
                                                                    if d <= self.distance:
                                                                        # relevant image is too similar too the query
                                                                        print("     DUPLICATE: " + str(d) + "  ######################")
                                                                        if action == "save":
                                                                            # duplicates have yet to be saved, so we do that here
                                                                            self.save_duplicate(q_im, query, r_im, relevant)
                                                                            dup = ([relevant, r_subdir])
                                                                            duplicates.append(dup)
                                                                        elif action == "delete":
                                                                            # auto-delete is active, so anything that could be a duplicate
                                                                            # can be safely deleted
                                                                            self.delete_duplicate(r)
            num_dups = 0
            for dup in duplicates:
                num_dups += 1
            return duplicates, num_dups

    def save_duplicate(self, q_im, q_name, r_im, r_name):
        new_dir, _ = os.path.splitext(os.path.join(self.save_dir, q_name))
        dup_dir = new_dir + "/duplicates"

        if not os.path.isdir(new_dir):
            os.makedirs(new_dir)
            cv2.imwrite(new_dir + "/" + q_name, q_im)
            os.makedirs(dup_dir)
        # write the relevant image to duplicates
        cv2.imwrite(dup_dir + "/" + r_name, r_im)

    def save_error(self, im, name, path):
        err_dir = self.save_dir + "/errors"
        if os.path.isdir(err_dir):
            os.makedirs(err_dir)

        file_path = os.path.join(err_dir, name)
        # print("     file_path: " + file_path)
        cv2.imwrite(file_path, im)
        os.remove(os.path.join(path, name))

    def delete_duplicate(self, r, i):
        path = os.path.join(self.top_dir, r[1])
        del_im = os.path.join(path, r[0])
        os.remove(del_im)
        print("[INFO] DELETED " + str(i).zfill(4))
