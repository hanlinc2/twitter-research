# Script combines the daily hashtag counts files in two directories.
# It takes as input two directories containing files of daily hashtag
# counts. It then copies files in both direcoties to the target 
# directory and, in the process, combines the files that exist in 
# both directory.  

import lib.an_util as util
import sys
from os import listdir
from os.path import join
import shutil
    
if __name__ == '__main__':
    dir1, dir2, out_dir = util.check_input(sys.argv, 3, "")
    f1_set = set([f for f in listdir(dir1)])
    f2_set = set([f for f in listdir(dir2)])
    
    f12_set = f1_set.intersection(f2_set)
    f11_set = f1_set.difference(f12_set)
    f22_set = f2_set.difference(f12_set)

    print "joining overlaping hashtag files..."
    for f in f12_set:
	combine_dict = {} 
	day_set1, day_dict1 = util.load_name_val_pairs(
            join(dir1, f))
	day_set2, day_dict2 = util.load_name_val_pairs(
            join(dir2, f))
	for day in day_set1:
            combine_dict[day] = day_dict1[day] + day_dict2[day]
        util.write_dict(combine_dict, join(out_dir, f))

    print "copying non-overlaping hashtag files..."
    for f in f11_set:
        shutil.copyfile(join(dir1, f), join(out_dir, f))
    for f in f22_set:
        shutil.copyfile(join(dir2, f), join(out_dir, f))
