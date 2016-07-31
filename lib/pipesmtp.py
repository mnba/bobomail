import smtplib
from popen2 import popen2
from bobomailrc import smtp_host

SENDMAIL = smtp_host #"/usr/sbin/sendmail -bs"


class SocketDummy:

    def __init__(self, file):
	self.file = file
	self.send = self.file.write
	self.close = self.file.close

	
class FileDummy:
   
    def __init__(self, input, output):
	self.ifile = input
	self.ofile = output
	self.read = self.ifile.read
	self.readline = self.ifile.readline
	self.write = self.ofile.write

    def close(self):
	self.ifile.close()
	self.ofile.close()

	
class SMTP(smtplib.SMTP):
    
    def connect(self, host="doesnt_matter", port=0):
	r, w = popen2(SENDMAIL, 1)
	self.file = FileDummy(r, w)
	self.sock = SocketDummy(self.file)
	(code, msg) = self.getreply()
        if self.debuglevel > 0 : print "connect:", msg
        return (code, msg)

    

if __name__ == "__main__":
    s = SMTP()
    print s.connect()
    print s.help()
    print s.quit()
