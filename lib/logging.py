from time import strftime, time, localtime

def log(s, log_filename):
	logfile = open(log_filename, "a")
	ts = strftime("%T %D", localtime(time()))
	logfile.write("[%s] %s\n" % (ts, s))
	logfile.close()
