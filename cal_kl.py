# Script calculates the Kullback Liebler divergence value for all
# daily hashtag counts files in the given directory.
# It takes as input a directory containing daily hashtag counts files
# and a specified output file name. It then calculates the kl value for
# each hashtag and then write the results as space separated txt file.

import lib.an_util as util
import sys
from os import listdir
from os.path import join
import math
import numpy as np

MSG = ("Calculate the Kullback-Liebler divergence "
       "for all hashtags in given directory "
       "containing files of daily counts.\n"
       "usage: {} hashtag_directory output_file_name").format(
           sys.argv[0])

def cal_kl(directory, ht_file, ht_kl):
    """kl is the expectation of the log difference between
       probabilities p and q.
       The formula for calculating kl is:
           kl = sum[ p(i) * ln(p(i)/q(i)) ]
       where p(i) is the normalized counts of i and q(i) is the
       uniform counts"""

    ht_set, ht_dict = util.load_name_val_pairs(
	join(directory, ht_file))
    days = len(ht_dict)
    kl = 0
    uniform = float(1)/days
    total_count = 0
    for ht in ht_dict:
        total_count += ht_dict[ht]
    for ht in ht_dict:
        norm = float(ht_dict[ht])/total_count
        if norm == 0:
            continue # log(0) is undef, set to 0
        kl += norm * math.log(norm / uniform)
    ht_kl[ht_file] = kl

if __name__ == '__main__':
    directory, out_fn = util.check_input(sys.argv, 2, MSG)

    ht_kl = {}
    for ht_file in listdir(directory):
        cal_kl(directory, ht_file, ht_kl)
    sorted_tup_ls = util.sort_dict(ht_kl)
    util.write_tup_ls(sorted_tup_ls, out_fn)
