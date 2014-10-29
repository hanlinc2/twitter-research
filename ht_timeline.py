# Script for extracting the daily count for specified hashtags in a file
# 	Takes in input file name and directory of filtered tweets-files, 
# 	extract the date from the file name and counts the occurances of
# 	all hashtag for the day. Write the results for each hashtag to 
# 	separate output files. 

import lib.an_util as util
import sum_hashtags as sumht
import json
import sys
from os import listdir
from os.path import isfile, join

DECODER = json.JSONDecoder()

def get_date(input_file):
	"""Generate the date in string based on the name of the input file"""
	basename, ext = input_file.split(".")
	return basename

def get_dates(input_ls):
	"""Process a ls of file and returns a list of dates"""
	rt_ls = []
	for f in input_ls:
		rt_ls.append(get_date(f))
	return rt_ls

def get_sorted_file_ls(directory):
	"""Returns a list of valid tweet-files sorted by name"""
	file_ls = [f for f in listdir(directory) if f != ".DS_Store"]
	file_ls.sort()
	return file_ls

def proc_daily_ht(in_fd, user_set):
	"""Returns a dictionary containing hashtags 
	   and their counts per file(day)"""
	ht_daily_count = {}	
	ht_daily_count_set = set() # use for membership check

	# read line by line and count each hashtag
	for line in in_fd:
		json_obj = json.loads(line.strip())

		# filtering for specific set of users
		if str(json_obj['user']['user_id']) not in user_set:
			continue

		# iterate through the list and update hashtag dictionary
		hashtag_obj_ls = json_obj["hashtags"]
		for hashtag_obj in hashtag_obj_ls:
			# field name for hashtag names is "text" 
			# must first become lower-case before encode	
			hashtag = hashtag_obj["text"].lower().encode('utf-8') 
			if hashtag in ht_daily_count_set: 
				ht_daily_count[hashtag] += 1
			else:
				ht_daily_count[hashtag] = 1
				ht_daily_count_set.add(hashtag)
	return [ht_daily_count, ht_daily_count_set]

def update_ht_counts(day_count, ht_dict, ht_daily_count_set,
					 ht_daily_count):
	"""update the ht_dict via ht_daily_count"""

	# keeps track of the hashtags already updated
	updated_hashtags = set()

	# update hashtags currently in ht_dict
	for hashtag in ht_dict:
		if hashtag in ht_daily_count_set: 
			updated_hashtags.add(hashtag)
			daily_count = ht_daily_count[hashtag]
			ht_dict[hashtag].append(daily_count)
		else:
			# hashtag not mentioned for this day
			ht_dict[hashtag].append(0) 

	# add hashtags that are not curently in ht_dict
	to_add = ht_daily_count_set.difference(updated_hashtags)
	for hashtag in to_add:
		ht_dict[hashtag] = [0]*(day_count-1)
		ht_dict[hashtag].append(ht_daily_count[hashtag])

def build_hashtag_dict(file_ls, user_set):
	ht_dict = {} # is a dictionary of {hashtag:list}
				 # list is the count for the hashtag on each day

	day_count = 1 # tracks number of day

	# iterate through the file-list and build the ht_dict
	for f in file_ls:
		print "loading {}...".format(f) 
		try:
			with open(join(directory, f)) as in_fd:
				ht_daily_count, ht_daily_count_set = proc_daily_ht(
					in_fd, user_set)
				update_ht_counts(
					day_count, ht_dict, ht_daily_count_set, 
					ht_daily_count)
			in_fd.closed
		except IOError as e:
			print e
		day_count += 1

	return ht_dict

def record(dates, ht_dict, dest_dir):
	"""Record dictionary of hashtag to output files"""
	print "recording hashtag timelines..."
	num_days = len(dates)
	for hashtag in ht_dict:
		out_file = hashtag
		try:
			with open(join(dest_dir, out_file), "w") as out_fd:
				daily_count_ls = ht_dict[hashtag]
				if len(daily_count_ls) != num_days: 
					print ("ALERT: days and counts mismatch" 
						"for hashtag {}").format(hashtag)
					continue
				for i in range(num_days):
					out_fd.write("{} {}\n".format(
						dates[i], str(daily_count_ls[i])))
			out_fd.closed
		except IOError as e:
			print "{}: {}".format(out_file, e)

if __name__ == "__main__":
	"""The main program"""
	orig_file, rt_file, directory, dest_dir = util.check_input(
		sys.argv, 4, "")
	user_set = an_util.load_usrs_csv(orig_file)
	user_set = user_set.union(an_util.load_usrs_csv(rt_file))
	print "number of users original & retweet users", len(user_set)
	file_ls = get_sorted_file_ls(directory)
	dates = get_dates(file_ls)
	print "number of days:", len(dates)
	ht_dict = build_hashtag_dict(file_ls, user_set)
	record(dates, ht_dict, dest_dir)
	sumht.sum_ht(dest_dir, "sorted_ht_counts.txt")
