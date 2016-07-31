# makehtml:
# This script generates the BoboMail Homepage
# from the text files in the docs directory

from bobomailrc import app_dir, pathjoin, bobomail_version
from bobomailrc import template_template, image_dir
import string, re
from cgi import escape

doc_dir = pathjoin(app_dir, "docs")

urlpat = re.compile(r'(\w+://[^>)\s]+)')
emailpat = re.compile(r'([-+,.\w]+@[-+.\w]+)')

def formatHTML(data):
	inList = 0
	html = ""
	data = string.replace(data, "\n\n\n", "\n \n")
	paragraphs = string.split(data, "\n\n")
	if paragraphs:
		if "\n" not in paragraphs[0]:
			html = html + "<h2>%s</h2>\n\n" % paragraphs[0]
			del paragraphs[0]
		for p in paragraphs:
			if len(p) and string.strip(p)[0] == "*":
				if not inList:
					html = html + "<ul>\n"
					inList = 1
				html = html + "\t<li>%s\n" % makelinks(string.strip(p)[1:])
			else:
				if inList:
					html = html + "</ul>\n\n"
					inList = 0
				if len(p) and p[0] == " ": html = html + "<pre>%s</pre>" % makelinks(p)
				elif p == " ": html = html + "\n<br>\n"
				else: html = html + "<p>\n\t%s\n</p>\n\n" % makelinks(p)
	if inList: html = html + "</ul>\n"
	return html

def makelinks(data):
	start, links = 0, {}
	data = escape(data)
	while 1:
		found = emailpat.search(data[start:])
		if found:
			url = found.group(1)
			links[url] = '<a href="mailto:%s">%s</a>' % (url, escape(url))
		else:
			found = urlpat.search(data[start:])
			if found:
				url = found.group(1)
				links[url] = '<a href="%s">%s</a>' % (url, escape(url))
			else: break
		start = start + found.end()
	for old, new in links.items():
		data = string.replace(data, old, new)
	return data


panel = """
    <br><p>
	<a style="text-decoration: none" href="http://sourceforge.net/project/?group_id=4938"><font color="white" size="-1" face="Arial, Helvetica, Sans Serif">Project page</font></a><br>
	<a style="text-decoration: none" href="http://sourceforge.net/bugs/?group_id=4938"><font color="white" size="-1" face="Arial, Helvetica, Sans Serif">Bug tracking</font></a><br>
	<a style="text-decoration: none" href="http://sourceforge.net/patch/?group_id=4938"><font color="white" size="-1" face="Arial, Helvetica, Sans Serif">Patch manager</font></a><br>
	<a href="http://sourceforge.net/mail/?group_id=4938"><font color="white" size="-1" face="Arial, Helvetica, Sans Serif">Mailing list</font></a><br>
	<br><br><br>
	<a style="text-decoration: none" href="images/shot1.gif"><font color="white" size="-1" face="Arial, Helvetica, Sans Serif">Screenshot 1</font></a><br>
	<a style="text-decoration: none" href="images/shot2.gif"><font color="white" size="-1"face="Arial, Helvetica, Sans Serif">Screenshot 2</font></a><br><br>
        <!--<a style="text-decoration: none" href="http://bobomail.sourceforge.net/cgi-bin/bobomail.cgi"><font size="-1" color="white" face="Arial, Helvetica, Sans Serif"><i><b>Test DEMO!</b></i></font></a><br><br>-->
	<a style="text-decoration: none" href="http://sourceforge.net/project/showfiles.php?group_id=4938"><font color="white" face="Arial, Helvetica, Sans Serif">Download</font></a><br><br>
        <a style="text-decoration: none" href="http://cvs.sourceforge.net/cvstarballs/bobomail-cvsroot.tar.gz"><font size="-2" color="white">Daily CVS Snapshot</font></a>
	</br></p>
"""

def genPage():
	files = ["README", "INSTALL", "PROBLEMS", "TODO", "ChangeLog", "THANKS", "CREDITS"]
	page = '<h1 align="center"><font color="darkblue">BoboMail %s</font><br><img alt="BoboMail" src="%s/bobomail.jpg"></h1>\n\n' % (bobomail_version, image_dir)
	navbar = "\n\t<h4><b>"
	for filename in files:
		navbar = navbar + '<a href="#%s">%s</a> | ' % (filename, filename)
		fn = pathjoin(doc_dir, filename)
		page = page + '<a name="%s"></a>' % filename
		page = page + formatHTML(open(fn).read())
		page = page + "<br>"
	navbar = navbar[:-2] + "<hr noshade></b></h4>\n"
	body = navbar + page

	from DocumentTemplate import HTMLFile
	import gttag
	html = HTMLFile(template_template)
	htmlcode = html(title="Homepage", imagedir="images/", cgi="")
	return string.replace(string.replace(htmlcode, "%(body)s", body), "%(panel)s", panel)

if __name__ == "__main__":
	print genPage()
