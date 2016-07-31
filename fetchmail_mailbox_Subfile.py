# fetchmail_mailbox_Subfile.py
#  created  specially for fetchmail.py file to run
# FIXME: temporary solution!
#  src from  http://opensource.apple.com/source/python/python-4.2/python/Lib/mailbox.py
# created my MA (c&p)

class _Subfile:

    def __init__(self, fp, start, stop):
        self.fp = fp
        self.start = start
        self.stop = stop
        self.pos = self.start

    def read(self, length = None):
        if self.pos >= self.stop:
            return ''
        remaining = self.stop - self.pos
        if length is None or length < 0:
            length = remaining
        elif length > remaining:
            length = remaining
        self.fp.seek(self.pos)
        data = self.fp.read(length)
        self.pos = self.fp.tell()
        return data

    def readline(self, length = None):
        if self.pos >= self.stop:
            return ''
        if length is None:
            length = self.stop - self.pos
        self.fp.seek(self.pos)
        data = self.fp.readline(length)
        self.pos = self.fp.tell()
        return data

    def readlines(self, sizehint = -1):
        lines = []
        while 1:
            line = self.readline()
            if not line:
                break
            lines.append(line)
            if sizehint >= 0:
                sizehint = sizehint - len(line)
                if sizehint <= 0:
                    break
        return lines

    def tell(self):
        return self.pos - self.start

    def seek(self, pos, whence=0):
        if whence == 0:
            self.pos = self.start + pos
        elif whence == 1:
            self.pos = self.pos + pos
        elif whence == 2:
            self.pos = self.stop + pos

    def close(self):
        del self.fp
        
