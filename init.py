import os, sys

try:
    from bobomailrc import *
except:
	print "Content-type: text/plain\n"
	print "Serious error:\n\n"
	print "You made a syntax error in your configuration file bobomailrc.py"
	print "Please correct this. To see the error, just execute bobomailrc.py"
	print "this way:"
	print "cd /usr/local/bobomail"
	print "python bobomailrc.py\n\n"
	sys.exit(1)

found_error = 0

import stat
def checkfile(fn, perm):
	global found_error
	try: st = os.stat(fn)
	except: return
	mode = stat.S_IMODE(st[stat.ST_MODE])
	owner = st[stat.ST_UID]
	user = os.getuid()
	group = os.getuid()
	if mode != perm or owner != user:
		try:
			os.chmod(fn, mode)
			os.chown(fn, user, group)
			return
		except: pass
		if not found_error:
			print "Content-type: text/plain\n"
			print "Security error:\n\n"
		print "%s has the wrong file permissions" % fn
		print "or is not owned by the current process"
		print "  The fix this type:"
		print "    chmod %o %s" % (perm, fn)
		print "    chown %s.%s %s\n\n"  % (user, os.getgid(), fn)
		found_error = 1
		
checkfile(var_dir, 448)
checkfile(var_dir, 448)
checkfile(session_db_filename, 384)
checkfile(session_db_filename + ".dat", 384)
checkfile(session_db_filename + ".dir", 384)
checkfile(user_db_filename, 384)
checkfile(user_db_filename + ".dat", 384)
checkfile(user_db_filename + ".dir", 384)
checkfile(log_filename, 384)
if found_error:
	sys.exit(1)

sys.path.append(pathjoin("app_dir", "lib"))


os.environ["LANGUAGE"] = language

import fintl
gettext = fintl.gettext
fintl.bindtextdomain("bobomail", locale_dir)
fintl.textdomain("bobomail")
i18n = gettext
