from os import listdir, path 
import json
import operator


def check_input(argv, arg_length, msg):
	if len(argv) != arg_length + 1:
		print msg
		exit(1)
	else:
		return argv[1:]


def load_usrs_csv(input_file):
	"""Load the csv in given file into a set"""
	usr_set = set()
	try:
		with open(input_file) as in_fd:
			content = in_fd.readline()
			usr_ls = content.strip().split(",")
			usr_set = set(usr_ls)
		in_fd.closed
	except IOError as e:
		print e
	return usr_set

def load_name_val_pairs(input_file, num_type = "int", start_thr=0, end_thr=-1):
	"""Load the given name-value pairs in given file into a dict and a set"""
	output_set = set()
	output_dict = {}
	try:
		with open(input_file) as in_fd:
			if num_type == "fl":	
				for line in in_fd:
					line = line.strip()
					usr_str, count_str = line.split(" ")
					count = float(count_str)
					if ((end_thr != -1 and count >= end_thr) or 
							count < start_thr): continue
					if usr_str in output_set:
						output_dict[usr_str] += float(count)
					else:
						output_set.add(usr_str)
						output_dict[usr_str] = float(count)
			else:
				for line in in_fd:
					line = line.strip()
					usr_str, count_str = line.split(" ")
					count = int(count_str)
					if ((end_thr != -1 and count > end_thr) or 
							count < start_thr): continue
					if usr_str in output_set:
						output_dict[usr_str] += int(count)
					else:
						output_set.add(usr_str)
						output_dict[usr_str] = int(count)
		in_fd.closed
	except IOError as e:
		print e
	return output_set, output_dict

def gen_file_name(input_name, addon):
	"""Generate output file name with the addon"""
	file_path, filename = path.split(input_name)
	basename, ext = filename.split(".")
	new_name = basename + addon + "." + ext
	return new_name

def write_ls(input_ls, output_file):
	try:
		with open(output_file, "w") as out_fd:
			print "writing to {}...".format(output_file)
			ret_str = "\n".join(input_ls)
			out_fd.write(ret_str)
			print "done"
		out_fd.closed
	except IOError as e:
		print e
		
def write_set(input_set, output_file):
	"""Record the given set"""
	try:
		with open(output_file, "w") as out_fd:
			print "writing to {}...".format(output_file)
			result_ls = []
			for item in input_set:
				result_ls.append(item)	
			output_str = ",".join(result_ls)
			out_fd.write("{}\n".format(output_str))
			print "done"
		out_fd.closed
	except IOError as e:
		print e

def write_dict(input_dict, output_file):
	"""Record the given dictionary"""
	try:
		with open(output_file, "w") as out_fd:
			print "writing to {}...".format(output_file)
			for item in input_dict:
				out_fd.write("{} {}\n".format(item, input_dict[item]))
			print "done"
		out_fd.closed
	except IOError as e:
		print e

def write_tup_ls(input_tup_ls, output_file):
	"""Record the given list of tuples"""
	try:
		with open(output_file, "w") as out_fd:
			print "writing to {}...".format(output_file)
			for tup in input_tup_ls:
				name, val = tup
				out_fd.write("{} {}\n".format(name, val))
			print "done"
		out_fd.closed
	except IOError as e:
		print e

def update_dict(usrid, usr_set, usr_dict):
    """update dictionary and set"""
    if usrid in usr_set:
        usr_dict[usrid] += 1
    else:
        usr_set.add(usrid)
        usr_dict[usrid] = 1

def file_count_rtts(input_file, filter_set, count_dict, count_set, total_counts):
    """Extract total retweets and a subset's retweets from a given json buffer"""
    try:
        with open(input_file) as in_fd:
            for line in in_fd:
                obj = json.loads(line.strip())
                if "retweeted_status" in obj: # tweet is a retweet
	            	total_counts += 1 # counting the total number of retweets
                	if filter_set: # count tweets for a given user set
						userid = str(obj['user']['user_id'])
						if userid in filter_set:
							update_dict(usrid, count_set, count_dict)
        in_fd.closed
    except IOError as e:
        print e
    return total_counts

def dir_count_rtts(directory, given_usrs_set):
    """Count retweets of all files in a dictionary"""
    file_ls = [f for f in listdir(directory) if path.isfile(path.join(directory, f)) and f != ".DS_Store"]
    tts_count = 0
    count_dict = {}
    count_set = set()
    for f in file_ls:
        print "loading {}...".format(f)
        tts_count = file_count_rtts(path.join(directory, f), given_usrs_set, count_dict, count_set, tts_count)
    return [tts_count, count_dict]

def get_rt(f, usr_set, usr_dict, in_usr_set):
    """Extract users who retweeted a given set of users"""
    try:
        with open(f) as in_fd:
            for line in in_fd:
                obj = json.loads(line.strip())
                if "retweeted_status" in obj: # tweet is a retweet
                    if in_usr_set: # we are filtering for a given user set
                        retweeted_usrid = str(obj['retweeted_status']['user']['user_id'])
                        if retweeted_usrid in in_usr_set: 
                            usrid = str(obj['user']['user_id'])
                            update_dict(usrid, usr_set, usr_dict)
                    else: # no filter
                        usrid = str(obj['user']['user_id'])
                        update_dict(usrid, usr_set, usr_dict)
        in_fd.closed
    except IOError as e:
        print e

def dir_get_rt(directory, in_usr_set):
    """Get a dictionary of all usr id's and corresponding counts"""
    file_ls = [f for f in listdir(directory) if path.isfile(path.join(directory, f)) and f != ".DS_Store"]
    usr_dict = {}
    usr_set = set() # for checking membership 
    for f in file_ls:
        print "loading {}...".format(f)
        get_rt(path.join(directory, f), usr_set, usr_dict, in_usr_set)
    return usr_dict 

def sort_dict(input_dict, sort_idx=1, is_reverse=True):
    sorted_tuples = sorted(input_dict.iteritems(), 
    					   key=operator.itemgetter(sort_idx),
    					   reverse=is_reverse)
    return sorted_tuples


