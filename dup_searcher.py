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
            for query_top, query_subdirs, _ in os.walk(self.top_dir):
                for q_subdir in query_subdirs:
                    q_path = os.path.join(query_top, q_subdir)
                    for _, _, q_images in os.walk(q_path):
                        for query in q_images:
                            # get query image from a subdirectory of the top level
                            print("[INFO] Query #" + str(i).zfill(7) + ": " + query)
                            q = os.path.join(q_path, query)
                            q_im = cv2.imread(q)

                            # set the save and duplicates directories to be used in each histogram comparison
                            self.new_dir, _ = os.path.splitext(os.path.join(self.save_dir, query))
                            self.dup_dir = self.new_dir + "/duplicates"
                            i += 1

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
                                                r = os.path.join(r_path, relevant)

                                                # asserts that relevant is not an iteration of the query
                                                if not q == r:
                                                    r_im = cv2.imread(r)
                                                    q_features = self.desc.describe(q_im)
                                                    r_features = self.desc.describe(r_im)

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

            empty = False
            num_dups = len(duplicates)
            if num_dups < 1:
                empty = True
            return duplicates, empty, num_dups

    def save_duplicate(self, q_im, q_name, r_im, r_name):
        if not os.path.isdir(self.new_dir):
            os.makedirs(self.new_dir)
            cv2.imwrite(self.new_dir + "/" + q_name, q_im)
            os.makedirs(self.dup_dir)
        # write the relevant image to duplicates
        cv2.imwrite(self.dup_dir + "/" + r_name, r_im)

    def delete_duplicate(self, r, i):
        path = os.path.join(self.top_dir, r[1])
        del_im = os.path.join(path, r[0])
        os.remove(del_im)
        print("[INFO] DELETED " + str(i).zfill(4))
