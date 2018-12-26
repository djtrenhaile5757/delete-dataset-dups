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
        self.duplicates = list()
        self.errors = list()

    def gather_duplicates(self, action, save_del=False, i=1):
        if save_del:
            i = 1
            for dup in self.duplicates:
                self.delete_duplicate(dup, i)
                i += 1

        else:
            # right now, cannot walk save directory to check for discarded possible dups
            for query_top, query_subdirs, _ in os.walk(self.top_dir):
                for q_subdir in query_subdirs:
                    q_path = os.path.join(query_top, q_subdir)
                    for _, _, q_images in os.walk(q_path):
                        for query in q_images:
                            q_i = 1
                            del_i = 1
                            # get query image from a subdirectory of the top level
                            if not self.is_error_image(q_subdir + "/" + query):
                                print("[INFO] Query #" + str(q_i).zfill(7) + ": " + query)
                                q_i += 1

                                q = os.path.join(q_path, query)
                                q_im = cv2.imread(q)
                                err, q_features = self.get_features(q_im, query_top, q_subdir, query)
                                dup_query = self.check_dup_query(q_subdir + "/" + query)

                                # ** checks that the image query did not error out or
                                # was a second iteration of a previously identified duplicate
                                if not err or dup_query:
                                    for relevant_top, relevant_subdirs, _ in os.walk(self.top_dir):
                                        for r_subdir in relevant_subdirs:
                                            r_path = os.path.join(relevant_top, r_subdir)
                                            for _, _, r_images in os.walk(r_path):
                                                for relevant in r_images:
                                                    # get a new comparison image
                                                    r = os.path.join(r_path, relevant)

                                                    # same error assertion, plus a check that the relevant image
                                                    # is not another iteration of the query
                                                    if not self.is_error_image(r_subdir + "/" + relevant) or not q == r:
                                                        r_im = cv2.imread(r)
                                                        err, r_features = self.get_features(r_im, relevant_top,
                                                                                            r_subdir, relevant)

                                                        if not err:
                                                            d = dists.chi2_distance(r_features, q_features)
                                                            if d <= self.distance:
                                                                # relevant image is too similar too the query
                                                                print("     DUPLICATE: " + str(d) + "  ################"
                                                                                                    "######")
                                                                if action == "save":
                                                                    # save the duplicate
                                                                    self.save_duplicate(q_im, query, r_im, r_subdir,
                                                                                        relevant)

                                                                elif action == "delete":
                                                                    # auto-delete is active, so anything that could
                                                                    # be a duplicate can be safely deleted
                                                                    self.delete_duplicate(r, del_i)
                                                                    del_i += 1
            num_dups = 0
            for dup in self.duplicates:
                num_dups += 1
            return num_dups

    def get_features(self, im, top, subdir, name):
        try:
            return False, self.desc.describe(im)
        except cv2.error as e:
            print(e)
            print("[INFO] Error on query image: " + subdir + "/" + name)
            print("     adding to error photos in save directory")

            path = os.path.join(top, subdir)
            self.save_error(im, name, path)
            return True, _

    def save_duplicate(self, q_im, q_name, r_im, r_subdir, r_name):
        new_dir, _ = os.path.splitext(os.path.join(self.save_dir, q_name))
        dup_dir = new_dir + "/duplicates"

        if not os.path.isdir(new_dir):
            os.makedirs(new_dir)
            cv2.imwrite(new_dir + "/" + q_name, q_im)
            os.makedirs(dup_dir)
        # write the relevant image to duplicates
        cv2.imwrite(dup_dir + "/" + r_name, r_im)
        self.duplicates.append(r_subdir + "/" + r_name)

    def check_dup_query(self, q):
        for dup in self.duplicates:
            if q == dup:
                # the image has already been identified as a duplicate of another
                # and can therefore be safely ignored
                return True
        return False

    def is_error_image(self, im_name):
        for error in self.errors:
            if im_name == error:
                return True
        return False

    def save_error(self, im, name, path):
        err_dir = self.save_dir + "/errors"
        if os.path.isdir(err_dir):
            os.makedirs(err_dir)

        file_path = os.path.join(err_dir, name)
        # print("     file_path: " + file_path)
        cv2.imwrite(file_path, im)
        os.remove(os.path.join(path, name))

        subdir = os.path.basename(path)
        self.errors.append(subdir + "/" + name)

    @staticmethod
    def delete_duplicate(r, i):
        os.remove(r)
        print("[INFO] DELETED " + str(i).zfill(4))
