import lib.an_util as util
import sys
from os import listdir
from os.path import join

def sum_ht(ht_dir, out_fn):
    hashtag_dict = {}
    for f in listdir(ht_dir):
        count = 0
        try:
            with open(join(ht_dir, f)) as in_fd:
                for line in in_fd:
                    date, c = line.strip().split(" ")
                    count += int(c)
            in_fd.closed
        except IOError as e:
            print e
        hashtag_dict[f] = count        
    sorted_ls = util.sort_dict(hashtag_dict)
    util.write_tup_ls(sorted_ls, out_fn)

if __name__ == '__main__':
    ht_dir, out_fn = util.check_input(sys.argv, 2, "")
    sum_ht(ht_dir, out_fn)
