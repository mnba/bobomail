import re, sys
assignment = re.compile('^([a-z][_a-z0-9]*)[\t ]*=[\t ](".*")(.*)', re.I)


settings = [
	("app_dir", "/usr/local/bobomail", "Enter here the directory where you have installed BoboMail"),
	("pop3_host", "localhost", "Choose POP3-host where the messages are stored"),
	("smtp_host", "localhost", "Choose SMTP-host to use for outgoing messages"),
	("domain", "localdomain", "Set domain for form-header"),
	("image_dir", "/bobomail", "Set directory relative to DocumentRoot where the contents of app_dir/images are"),
	("language", "en_EN", "Change BoboMail's language (en_EN, de_DE or pt_BR)")
	]

print

try:
	lines = open("/usr/local/bobomail/bobomailrc.py").readlines()
except:
	print "Error: could not load configuration data from bobomailrc.py"
	sys.exit(1)
	
print "BoboMail-setup"
print "=============="
print
print "This setup will change the important variables in bobomailrc.py"
print "You might want to look into this file to customize even more BoboMail"
print "To use the suggested default just press <Return>"
print

for (entry, default, help) in settings:
	for i in range(len(lines)):
		line = lines[i]
		found = assignment.match(line)
		if found:
			key, value, rest = found.group(1), found.group(2), found.group(3)
			if key == entry:
				print
				print help
				print "  current setting: %s" % value
				print '  default setting: "%s"' % default
				print "  ",
				newvalue = raw_input("%s = " % key)
				lines[i] = '%s = "%s"%s\n' % (key, newvalue or default or value, rest)
				print " new line:", lines[i]

print
try:
	open("bobomailrc.py", "w").writelines(lines)
	print "Ready. Have fun :-)"
except:
	print "Error: configuration could not be saved to bobomailrc.py"
	sys.exit(1)
print

