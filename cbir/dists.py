# import the necessary packages
import numpy as np


def chi2_distance(hist_a, hist_b, eps=1e-10):
	# compute the chi-squared distance
	d = 0.5 * np.sum(((hist_a - hist_b) ** 2) / (hist_a + hist_b + eps))

	# return the chi-squared distance
	return d
