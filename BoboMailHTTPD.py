#!/usr/bin/env python
##############################################################################
# 
# Zope Public License (ZPL) Version 0.9.5
# ---------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Any use, including use of the Zope software to operate a website,
#    must either comply with the terms described below under
#    "Attribution" or alternatively secure a separate license from
#    Digital Creations.  Digital Creations will not unreasonably
#    deny such a separate license in the event that the request
#    explains in detail a valid reason for withholding attribution.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# Attribution
# 
#   Individuals or organizations using this software as a web site must
#   provide attribution by placing the accompanying "button" and a link
#   to the accompanying "credits page" on the website's main entry
#   point.  In cases where this placement of attribution is not
#   feasible, a separate arrangment must be concluded with Digital
#   Creations.  Those using the software for purposes other than web
#   sites must provide a corresponding attribution in locations that
#   include a copyright using a manner best suited to the application
#   environment.  Where attribution is not possible, or is considered
#   to be onerous for some other reason, a request should be made to
#   Digital Creations to waive this requirement in writing.  As stated
#   above, for valid requests, Digital Creations will not unreasonably
#   deny such requests.
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
##############################################################################
"""Simple Bobo HTTP Server (based on CGIHTTPServer.py)

What's Bobo?

  An open source collection of tools for developing
  world-wide web applications in Python. Find out more at
  http://www.digicool.com/releases/bobo/

What's Zope?

  Zope is the result of the merging of Bobo and Principia.
  For more info visit the Zope web site at
  http://www.zope.org/

What does ZopeHTTPServer.py do?

  It is a very simple web server that published a module 
  with Bobo. ZopeHTTPServer.py is probably the easiest way
  to publish a module with Bobo. It does not require anything
  besides Python and Bobo to be installed. It is fast because
  it publishes a module as a long running process.

Why not use CGI or PCGI or Medusa?

  ZopeHTTPServer is much simpler to use than other Bobo publishers.
  ZopeHTTPServer does not require any configuration. It has a 
  friendly license. It also offers excellent performance, threaded
  publishing, and streaming response, not to mention all the Bobo
  basics like authenication, control of response content-type,
  file uploads, etc.

Features:

  -Only publishes one module at a time
  -Cannot reload a module
  -Does not serve files or CGI programs, only Bobo
  -Single-threaded or multi-threaded publishing
  -Unbuffered output so response can stream
  -Works under Python 1.5 and Python 1.4 (mostly) 
  -At least it's easy to use

Basic Useage:

  ZopeHTTPServer.py <path to module>

  This publishes your module on the web.

Usage:

  ZopeHTTPServer.py [-p <port>] [-t] [-h <host address>] <path to module> [var=value,]

  Starts a web server which publishes the specified module.

  -p <port>: Run the server on the specified port. The default
  port is 9673.

  -t: Use a multi-threaded HTTP server. The default is a
  single-threaded server. Note, your platform must support
  threads to use the multi-threaded server.

  -h: Specifies the host address. Python normally supplies this by default. 

  -P <pid file>: Specifies a file in which the server will write its PID

  -s <script_name>: Specify a virtual script name.

  Specifying additional arguments of the form var=value sets environment
  variables. You can use this facility to set things like BOBO_DEBUG_MODE=1
  and the like. These setting override default environment settings, so you
  can do things like change the SCRIPT_NAME or other weird stuff. NOTE:
  var=value settings can come before or after the path to module.

  You can also use the server from Python like this::

    import ZopeHTTPServer
    ZopeHTTPServer.main(<args>)

  The form the args take is exactly the same as the command line arguments.
  For example::

    ZopeHTTPServer.main("-t","-p 80","/home/amos/Test.py","BOBO_DEBUG_MODE=1")

Using ZopeHTTPServer behind Apache 

  ZopeHTTPServer doesn't have many fancy features, but it's easy to 
  use. Andreas Kostyrka suggests using ZopeHTTPServer with an Apache
  proxy to get some of Apache's cool features like SSL.
  
  Run ZopeHTTPServer on a high port and an IP address which is behind
  a firewall. For example 127.0.0.2, port 5000::
  
    ZopeHTTPServer -p 5000 -h 127.0.0.2 /home/amos/MyModule.py SCRIPT_NAME=/intern
  
  Then use Apache's proxy module to map requests to ZopeHTTPServer::
  
    RewriteEngine on
    RewriteRule ^/intern/(.*) http://127.0.0.2:5000/$1 [P]

  This rule maps request beginning with '/intern/' to ZopeHTTPServer.
  Notice that we set the ZopeHTTPServer SCRIPT_NAME to '/intern' so that
  it knows how it's being accessed. You can change other aspects of
  ZopeHTTPServer's environment to match the proxying environment. For example
  if you are using SSL, you should set HTTPS=on.

Known bugs:

  PUT doesn't work very well at all.
  
  REQUEST.write never closes the connection under Python 1.4

  There is a problem with mutipart/form-data POST requests
  under win32 and python 1.5.2a2. I think the problem is
  with cgi.py

  Under win32 interupted HTTP requests can raise exceptions,
  but they don't seem to cause any problems.
"""

__version__='$Revision: 1.1.1.1 $'[11:-2]

import SocketServer
import SimpleHTTPServer
import BaseHTTPServer
import os
import sys
import urllib
import string
import tempfile
import socket
try: from cStringIO import StringIO
except ImportError: from StringIO import StringIO


class ResponseWriter:
    """Logs response and reorders it so status header is
    first. After status header has been written, the rest
    of the response can stream."""
    
    def __init__(self,handler):
        self.handler=handler
        self.data=""
        self.latch=None
        
    def write(self,data):
        if self.latch:
            self.handler.wfile.write(data)
        else:
            self.data=self.data+data
            start=string.find(self.data,"Status: ")
            if start != -1:
                end=string.find(self.data,"\n",start)
                status=self.data[start+8:end]
                code, message=tuple(string.split(status," ",1))
                self.handler.send_response(string.atoi(code),message)
                self.handler.wfile.write(self.data[:start]+
                    self.data[end+1:])
                self.latch=1

    def flush(self):
        pass
    

class BoboRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Handler for GET, HEAD and POST. Only publishes one
    Bobo module at a time. All URLs go to the published module.
    Does not serve files or CGI programs.
    """
    
    server_version = "ZopeHTTP/" + __version__
    buffer_size = 8192
    env_override={}
    script=''

    def setup(self):
        """overrides defaults to set larger buffer for rfile
        otherwise large POST requests seem to take forever."""
        self.connection = self.request
        self.rfile = self.connection.makefile('rb', self.buffer_size)
        self.wfile = self.connection.makefile('wb', 0)

    def hack_si(self):
        #cgi.py doesn't like to parse file uploads unless we do this
        si_len=string.atoi(self.headers.getheader('content-length'))
        if si_len < 1048576:
            si=StringIO()
            si.write(self.rfile.read(si_len))
        else:
            bufsize=self.buffer_size
            si=tempfile.TemporaryFile()
            while si_len > 0:
                if si_len < bufsize:
                    bufsize=si_len
                data=self.rfile.read(bufsize)
                si_len=si_len - len(data)
                si.write(data)
        si.seek(0)
        self.rfile=si

    def do_POST(self):
        if string.find(self.headers.getheader('content-type'),
            'multipart/form-data') != -1:
            self.hack_si()
        self.publish_module()

    def do_GET(self):
        self.publish_module()

    def do_HEAD(self):
        #is this necessary?
        self.publish_module()
    
    def do_PUT(self):
        #doesn't work very well yet
        self.env_override['REQUEST_METHOD']='PUT'
        self.env_override['CONTENT_TYPE']='application/data'
        self.hack_si()
        self.publish_module()

    def publish_module(self):
        publish_module(
            self.module_name,
            stdin=self.rfile,
            stdout=ResponseWriter(self),
            stderr=sys.stderr,
            environ=self.get_environment())

    def get_environment(self):
        #Partially derived from CGIHTTPServer
        env={}
        env['SERVER_SOFTWARE'] = self.version_string()
        env['SERVER_NAME'] = self.server.server_name
        env['SERVER_PORT'] = str(self.server.server_port)
        env['SERVER_PROTOCOL'] = self.protocol_version
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        rest = self.path
        i = string.rfind(rest, '?')
        if i >= 0:
            rest, query = rest[:i], rest[i+1:]
        else:
            query = ''
        uqrest = urllib.unquote(rest)
	script=self.script
	if script:
	    env['SCRIPT_NAME'] = script[:-1]
	    if uqrest[:len(script)]==script:
		uqrest=uqrest[len(script)-1:]
	else: env['SCRIPT_NAME'] = ''
        env['PATH_INFO'] = uqrest
        env['REQUEST_METHOD'] = self.command
        env['PATH_TRANSLATED'] = self.translate_path(uqrest)
        if query:
            env['QUERY_STRING'] = query
        host = self.address_string()
        if host != self.client_address[0]:
            env['REMOTE_HOST'] = host
        env['REMOTE_ADDR'] = self.client_address[0]
        env['CONTENT_TYPE'] = self.headers.getheader('content-type')
        length = self.headers.getheader('content-length')
        if length:
            env['CONTENT_LENGTH'] = length
        # handle the rest of the environment
        for k,v in self.headers.items():
            k=string.upper(string.join(string.split(k,"-"),"_"))
            if not env.has_key(k) and v:
                env['HTTP_'+k]=v
        if self.env_override:
            for k,v in self.env_override.items():
                env[k]=v
        return env


class NonThreadingHTTPServer(BaseHTTPServer.HTTPServer):
    "The normal HTTPServer with some socket tweaks"
    
    def server_bind(self):
        # Modified version of server_bind that allows unconnected
        # win32 boxes to run the server without errors.
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        SocketServer.TCPServer.server_bind(self)
        host, port = self.socket.getsockname()
        hostname=host
        if not host or host == '0.0.0.0':
            host = socket.gethostname()
        try:
            hostname, hostnames, hostaddrs = socket.gethostbyaddr(host)
            if '.' not in hostname:
                for host in hostnames:
                    if '.' in host:
                        hostname = host
                        break
        except:
            pass
        self.server_name = hostname
        self.server_port = port

    def handle_request(self):
        """Handle one request, possibly blocking."""
        request, client_address = self.get_request()
        if self.verify_request(request, client_address):
            try:
                self.process_request(request, client_address)
            except SystemExit:
                self.handle_error(request, client_address)
                sys.exit(0)
            except:
                self.handle_error(request, client_address)

                
class ThreadingHTTPServer(SocketServer.ThreadingMixIn,
    NonThreadingHTTPServer):
    "A threading HTTPServer with some socket tweaks"
    pass


def try_to_become_nobody():
    # from CGIHTTPServer
    try: import pwd
    except: return
    try:
        nobody = pwd.getpwnam('nobody')[2]
    except pwd.error:
        nobody = 1 + max(map(lambda x: x[2], pwd.getpwall()))
    try: os.setuid(nobody)
    except os.error: pass    

def set_published_module(file,klass,env=None):
    dir,file=os.path.split(file)
    name,ext=os.path.splitext(file)
    klass.module_name=name
    klass.module_dir=dir
    cdir=os.path.join(dir,'Components')
    sys.path[0:0]=[dir,cdir,os.path.join(cdir,sys.platform)]
    
    if env is not None:
        klass.env_override=env
    
    global publish_module
    try:
        import ZPublisher
        publish_module=ZPublisher.publish_module
    except:
        import cgi_module_publisher
        publish_module=cgi_module_publisher.publish_module
        
    __import__(name) # to catch problem modules right away
    print "Publishing module %s" % name

def start(module_file, host='', port=8080, threading=None,env=None):
    set_published_module(module_file,BoboRequestHandler,env)
    server_address = (host, port)
    if threading:
        try:
            import thread
            httpd = ThreadingHTTPServer(server_address,
                BoboRequestHandler)
            print "Using threading server"
        except ImportError:
            httpd = NonThreadingHTTPServer(server_address,
                BoboRequestHandler)
    else:
        httpd = NonThreadingHTTPServer(server_address,
            BoboRequestHandler)
    print "Serving HTTP on port", port, "..."
    try_to_become_nobody()
    try:
        httpd.serve_forever()
    except:
        httpd.socket.close()
        sys.exit(1)

def die(message=''):
    if message: print '\nError: %s\n' % message
    print __doc__
    sys.exit(1)

def main(args=None):
    args=args or sys.argv[1:]
    import getopt
    optlist, args=getopt.getopt(args,"tp:h:P:s:")
    if len(args) < 1: die()

    env={}
    module_file=''
    for a in args:
        a=string.split(a,'=')
        if len(a)==1:
            if module_file: die('Unrecognized argument: %s' % a[0])
            module_file=a[0]
        elif len(a)==0: continue
        else:
            k, v = a[0], string.join(a[1:],'=')
            os.environ[k]=v
            env[k]=v

    port=9673
    threading=None
    host=''
    for k,v in optlist:
        if k=="-p":
            port=string.atoi(v)
        elif k=="-t":
            threading=1
        elif k=="-h":
            host=v
        elif k=="-P":
            open(v,'w').write(str(os.getpid()))
	elif k=='-s':
	    while v[:1]=='/': v=v[1:]
	    while v[-1:]=='/': v=v[:-1]
	    BoboRequestHandler.script="/%s/" % v
    start(module_file,host,port,threading,env)


if __name__=="__main__": 
    if os.environ.has_key("QUERY_STRING"):
		print "Content-type: text/plain\n"

    sys.path.insert(0, os.path.dirname(sys.argv[0]))
    import bobomailrc
    sys.path.insert(0, bobomailrc.app_dir)
    
    bobomailrc.image_dir = "GetFile?images"

    if "-d" in sys.argv:
	sys.stdout = sys.stderr = open(bobomailrc.access_log, "a")
	sys.argv.remove("-d")
		
    #remove "-t" if your Python-interpreter doesn't support threads
    main(["-p", str(bobomailrc.httpd_port), "main"])
