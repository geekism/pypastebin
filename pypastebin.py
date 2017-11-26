#!/usr/bin/python
#-*- coding: utf8 -*-

# 1. mkdir data
# 2. python pastebin-server.py &

import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
import argparse, uuid, os, urllib, cgi, telnetlib, sys, time, os, time, ssl, logging
import subprocess, random, os.path
from datetime import datetime
from OpenSSL import SSL

parser = argparse.ArgumentParser()
parser.add_argument('-s', action='store_true', default=False, dest='boolean_switch', help='Start with OpenSSL, Create With: openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365')
parser.add_argument('-p', action='store', dest='startport', type=int, help='Start on select port')
parser.add_argument('-b', action='store_true', default=False, dest='background', help='Start in the background')
parser.add_argument('-f', action='store', dest='sslcert', help='Select your myserver.pem')
parser.add_argument('-l', action='store', dest='listenip', help='Select Listening IP')
parser.add_argument('-u', action='store', dest='urlhost', help='subdomain.domain.com value')
parser.add_argument('-H', action='store', dest='eggdrop_host', help='Eggdrop Relay Hostname/IP')
parser.add_argument('-C', action='store', dest='eggdrop_chan', help='Eggdrop Relay Channel')
parser.add_argument('-P', action='store', dest='eggdrop_port', help='Eggdrop Port')
parser.add_argument('-L', action='store', dest='eggdrop_pass', help='Eggdrop Password')
parser.add_argument('-U', action='store', dest='eggdrop_user', help='Eggdrop Username')
parser.add_argument('-e', action='store_true',default=False, dest='enableegg', help='Enable eggdrop relay')
parser.add_argument('-v', action='version', version='%(prog)s 0.2.0')
results = parser.parse_args()

isfile = os.path.isfile
join = os.path.join

HTTP_PORT = results.startport
HTTP_IP = results.listenip
START_SSL = results.boolean_switch
SSL_CERT = results.sslcert
BACKGROUND = results.background
URLHOSTNAME = results.urlhost
RELAY = results.enableegg

if START_SSL == True:
   HEADER = "https://"
else:
   HEADER = "http://"

try:
  URLHOSTNAME
except NameError:
  print "Please define the URL with -u"
  quit()
else:
  print "Webserver URL is: \n"+HEADER+""+URLHOSTNAME+""

if RELAY == True:
	EHOST = results.eggdrop_host
	EPORT = results.eggdrop_port
	EPASSWD = results.eggdrop_pass
	EUSER = results.eggdrop_user
	ECHAN = results.eggdrop_chan
	URLHOSTNAME = results.urlhost
    	print "\nEggdrop Settings: \nHost: " + EHOST + ":" + EPORT + " \nUsername: " + EUSER + " \nPassword: ********** \nChannel: #" + ECHAN + ""

#if not os.path.exists('style.css'): open('style.css', 'w').close()
DIRECTORY = os.path.dirname(os.path.realpath(sys.argv[0]))

if BACKGROUND == True:
    PIDF = DIRECTORY + '/pastebin.pid'
    fpid = os.fork()
    if fpid!=0:
       fpid = os.fork()
       f = open(PIDF,'w')
       f.write(str(fpid))
       f.close()
       print "my pid:" + str(fpid)
       sys.exit(0)
       sys.argv[0] = 'pastebin'

class StreamToLogger(object):
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''
   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())

logging.basicConfig(
   level=logging.DEBUG,
   format='%(asctime)s:%(message)s',
   filename="pastebin.log",
   filemode='a'
)

stdout_logger = logging.getLogger('STDOUT')
sl = StreamToLogger(stdout_logger, logging.INFO)
sys.stdout = sl

stderr_logger = logging.getLogger('STDERR')
sl = StreamToLogger(stderr_logger, logging.ERROR)
sys.stderr = sl


PASTESCRIPT = """
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <link rel="stylesheet" type="text/css" href="%(CONTEXT_PATH)s/style.css">
    </head>
<CENTER>
<title>pure pasting!</title>
<a href=/>paste</a> - <a href=/about>about</a> - <a href=/changelog>changelog</a> - <a href=/pastebinit>paste post script</a>
</center>
<BR><BR><BR>

#!/usr/bin/perl<BR>
use warnings;<BR>
use LWP::UserAgent;<BR> 
use HTTP::Request::Common qw{ POST };<BR>
use CGI;<BR>
use WWW::Mechanize;<BR>
my $output = "";<BR>
my $pasteserver = " """+HEADER+""""""+URLHOSTNAME+"""";<BR>
@userinput = <STDIN>;<BR>
chomp (@userinput);<BR>
foreach $i (@userinput) { $output .= "$i\n"; }<BR>
my $url = "http://".$pasteserver."/create";<BR>
my $ua = LWP::UserAgent->new();<BR>
my $request = POST( $url, [ 'content' => $output ] );<BR>
my $redir = $ua->request($request);<BR>
my $gurl = $redir->header('Location');<BR>
my $content = $ua->request($request)->as_string();<BR>
my $cgi = CGI->new();<BR>
print "paste: http://".$pasteserver."".$gurl."\n";<BR>
</html>
"""

CHANGELOG = """
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <link rel="stylesheet" type="text/css" href="%(CONTEXT_PATH)s/style.css">
    </head>
<CENTER>
<title>pure pasting!</title>
<a href=/>paste</a> - <a href=/about>about</a> - <a href=/changelog>changelog</a> - <a href=/pastebinit>paste post script</a>
</center>
<BR><BR><BR>
11-16-2012: Project started.<br>
11-17-2012: paste script started.<br>
11-18-2012: paste script completed.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ added robots.txt to drop the crawlers<br>
11-19-2012: started adding content.<br>
11-25-2017: picked the project back up after finding it on a random USB stick<br>
</html>
"""

ABOUT = """
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <link rel="stylesheet" type="text/css" href="%(CONTEXT_PATH)s/style.css">
    </head>
<CENTER>
<title>pure pasting!</title>
<a href=/>paste</a> - <a href=/about>about</a> - <a href=/changelog>changelog</a> - <a href=/pastebinit>paste post script</a>
</center>
<BR><BR><BR>

py-pastebin: This is a project that i decided to pick up, and change to suite my needs, not<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;alot of pastebins offer its own pastebin dump script like i am doing<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;its nothing more then a mimic of paste.ubuntu.com and pastebinit script.
</html>
"""

FORM = """
<html class="html">
    <head>
	<link rel="stylesheet" type="text/css" href="style.css">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<link rel="stylesheet" type="text/css" href="http://shjs.sourceforge.net/lang/sh_$(LANG).css">
        <link rel="stylesheet" type="text/css" href="%(CONTEXT_PATH)s/style.css">

    </head>
<CENTER>
<title>pure pasting!</title>
<a href=/>paste</a> - <a href=/about>about</a> - <a href=/changelog>changelog</a> - <a href=/pastebinit>paste post script</a>
</center>
<BR><BR><BR>
<body color=#00000>
    <body style="font-size: 12">
        <form action="/create" method="POST">
            <textarea name="content" rows="20" class="content"></textarea>
            <BR><BR><a href="javascript:document.forms[0].submit()" class="button">Paste</a>
        </form>
    </body>
</html>
"""

ROBOT = """
User-agent: *<BR>
Disallow: /<BR>
Disallow: /adm/<BR>
Disallow: /administration/<BR>
Disallow: /admin/<BR>
Disallow: /adminportal/<BR>
Disallow: /drupal/<BR>
Disallow: /joomla/<BR>
"""

CONTENT_TEMPLATE = """
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <link rel="stylesheet" type="text/css" href="http://shjs.sourceforge.net/sh_style.css">
        <link rel="stylesheet" type="text/css" href="%(CONTEXT_PATH)s/style.css">

        <script src="http://shjs.sourceforge.net/sh_main.min.js" type="text/javascript"></script>
        <script type="text/javascript" src="http://shjs.sourceforge.net/lang/sh_%(LANG)s.js"></script>
    </head>
<CENTER>
<title>pure pasting!</title>
<a href=/>paste</a> - <a href=/about>about</a> - <a href=/changelog>changelog</a> - <a href=/pastebinit>paste post script</a>
</center>
<BR><BR><BR>
    <body onload="sh_highlightDocument();"><center>
        <ul id="lang_list_%(LANG)s">
            <li><a class="lang_desktop" href="%(CONTEXT_PATH)s/desktop/%(PASTEBIN_FILE_NAME)s">Desktop</a></li>
            <li><a class="lang_diff" href="%(CONTEXT_PATH)s/diff/%(PASTEBIN_FILE_NAME)s">DIFF</a></li>
            <li><a class="lang_makefile" href="%(CONTEXT_PATH)s/makefile/%(PASTEBIN_FILE_NAME)s">Makefile</a></li>
            <li><a class="lang_perl" href="%(CONTEXT_PATH)s/perl/%(PASTEBIN_FILE_NAME)s">PERL</a></li>
            <li><a class="lang_ruby" href="%(CONTEXT_PATH)s/ruby/%(PASTEBIN_FILE_NAME)s">Ruby</a></li>
            <li><a class="lang_xorg" href="%(CONTEXT_PATH)s/xorg/%(PASTEBIN_FILE_NAME)s">Xorg</a></li>
            <li><a class="lang_tcl" href="%(CONTEXT_PATH)s/tcl/%(PASTEBIN_FILE_NAME)s">TCL</a></li>
            <li><a class="lang_java" href="%(CONTEXT_PATH)s/java/%(PASTEBIN_FILE_NAME)s">Java</a></li>
            <li><a class="lang_python" href="%(CONTEXT_PATH)s/python/%(PASTEBIN_FILE_NAME)s">Python</a></li>
            <li><a class="lang_sql" href="%(CONTEXT_PATH)s/sql/%(PASTEBIN_FILE_NAME)s">Sql</a></li>
            <li><a class="lang_javascript" class="" href="%(CONTEXT_PATH)s/javascript/%(PASTEBIN_FILE_NAME)s">Javascript</a></li>
            <li><a class="lang_css" href="%(CONTEXT_PATH)s/css/%(PASTEBIN_FILE_NAME)s">Css</a></li>
            <li><a class="lang_html" href="%(CONTEXT_PATH)s/html/%(PASTEBIN_FILE_NAME)s">Html</a></li>
            <li><a class="lang_cpp" href="%(CONTEXT_PATH)s/cpp/%(PASTEBIN_FILE_NAME)s">Cpp</a></li>
            <li><a class="plain" href="%(CONTEXT_PATH)s/plain/%(PASTEBIN_FILE_NAME)s">Plain</a></li>
            <li><a class="last" href="%(CONTEXT_PATH)s/">Paste Again</a></li>
        </ul></center>
        <br style="clear: both"/>
	    <pre class="sh_%(LANG)s">%(CONTENT)s</pre>
    </body>
</html>
"""

STYLE_CSS = """
.html { }
body {	background: #000000; font-family: monospace; font-size: 12px; color: #1E90FF; }
a { color:#C0C0C0; text-decoration: none; }
a:hover { color: #fefefe; text-decoration: underline; }
textarea { font-family: 'Cantarell', serif; font-size: 16px; }
ul { display: block; text-shadow: none; height: 25px; margin: 0 0 0 -40; position: relative; float: center; }
li { display: inline; margin-left: 5px; }
li .last { margin-left: 30px; }
pre { font-family: 'Courier New'; font-size: 16px; text-shadow: none; background-color: white; margin-left: 5px; padding: 5px; border: 1px solid #C9D7F1; margin-top: -5px;}
.content { width: 80%; height: 80%; margin-left: 10%; margin-top: 1%; display: block; border: 3px solid #000; font-family: 'Courier New', Arial; }
.button { display:block; width:100px; height:50px; margin-left:45%; font-weight: bold; text-decoration: none; }
.ul_parent { position: absolute; }
#lang_list_java .lang_java, #lang_list_python .lang_python, #lang_list_javascript .lang_javascript, #lang_list_html .lang_html, #lang_list_css .lang_css, #lang_list_cpp .lang_cpp, #lang_list_sql .lang_sql, #lang_list_plain .lang_plain, #lang_list_desktop .lang_desktop, #lang_list_diff .lang_diff, #lang_list_makefile .lang_makefile, #lang_list_perl .lang_perl, #lang_list_ruby .lang_ruby, #lang_list_xorg .lang_xorg, #lang_list_tcl .lang_tcl { font-weight: bold; }
"""

DATA_FOLDER_NAME = "data"
DATA_FOLDER_PATH = "./" + DATA_FOLDER_NAME
URL_DATA_FOLDER = "/" + DATA_FOLDER_NAME + "/"
if not os.path.exists(DATA_FOLDER_NAME):
        os.makedirs(DATA_FOLDER_NAME)
        print time.asctime(), "Created pastebin data directory: ", DATA_FOLDER_NAME
PASTES = sum(1 for item in os.listdir(DIRECTORY) if isfile(join(DIRECTORY, item)))

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.init_params()
        if self.path not in ["/favicon.ico", "/style.css", URL_DATA_FOLDER]:
            self.log_request()

            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(FORM % {"CONTEXT_PATH": self.get_context_path()})
	    elif self.path == "/HEAD":
		DATE = time.strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime(time.time()))
		self.send_response(200)
		self.send_header("X-Powered By","PythonHTTPd")
		self.send_header("Content-Type", "text/html")
		self.send_header("Connection", "close")
		self.send_header("Date", DATE)
		self.send_header("Server", "PythonHTTPd")
		self.end_headers()
	    elif self.path == "/robots.txt":
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
		self.wfile.write(ROBOT % {"CONTEXT_PATH": self.get_context_path()})
	    elif self.path == "/changelog":
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
		self.wfile.write(CHANGELOG % {"CONTEXT_PATH": self.get_context_path()})
            elif self.path == "/pastebinit":
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(PASTESCRIPT % {"CONTEXT_PATH": self.get_context_path(),
                "CONTEXT_PATH": self.get_context_path()})
	    elif self.path == "/about":
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
		self.wfile.write(ABOUT % {"CONTEXT_PATH": self.get_context_path(),
		"CONTEXT_PATH": self.get_context_path()})
            elif self.path.find("/plain/") == 0:
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                filename = DATA_FOLDER_PATH + self.path[6:]
                content = self.read_file(filename)
                self.wfile.write(cgi.escape(content))
            elif len(self.path.split("/")) > 2:
                splits = self.path.split("/")
                lang = splits[1]
                self.pastebin_file_name = splits[2]
                filename = DATA_FOLDER_PATH + self.path[len(lang) + 1:]
		content = self.read_file(filename)
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(CONTENT_TEMPLATE % {"LANG": lang,
                    "CONTENT":cgi.escape(content),
                    "CONTEXT_PATH": self.get_context_path(),
                    "PASTEBIN_FILE_NAME": self.pastebin_file_name})
            else:
                self.pastebin_file_name = self.path[1:]
                filename = DATA_FOLDER_PATH + self.path
                if self.path.find(URL_DATA_FOLDER) == 0:
                    filename = "." + self.path
                content = self.read_file(filename)
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(CONTENT_TEMPLATE % {"LANG": "java",
                    "CONTENT":cgi.escape(content),
                    "CONTEXT_PATH": self.get_context_path(),
                    "PASTEBIN_FILE_NAME": self.pastebin_file_name})
        else:
            if self.path == "/style.css":
                self.log_request()
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(STYLE_CSS)
            else:
                return SimpleHTTPRequestHandler.do_GET(self)
    def do_POST(self):
        self.init_params()
        if self.path == "/create":
            filename = ''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890') for i in range(10)])
            f = open(DATA_FOLDER_PATH + "/" + filename, "w")
            f.write(self.params["content"])
            f.close()
            os.chmod(DATA_FOLDER_PATH + "/" + filename, 0666)
            self.send_response(301)
            self.send_header("Location", "/" + filename)
	    if RELAY == True:
                tn = telnetlib.Telnet(EHOST,EPORT,600)
                time.sleep(1)
                tn.read_until('Please enter your nickname.')
                tn.write(EUSER + '\n')
                tn.read_until('Enter your password.')
                tn.write(EPASSWD + '\n')
                tn.write(".msg #" + ECHAN + " new paste:\002 " + URLHOSTNAME + "" + filename + "\n")
                time.sleep(1)
                tn.write(".exit")
                self.end_headers()

    def read_file(self, filename):
        f = open(filename)
        content = f.read()
        f.close()
        return content

    def get_context_path(self):
    	if START_SSL == True:
           return "https://" + self.headers['host']
        else:
           return "http://" + self.headers['host']

    def init_params(self):
        """Get the params from url and request body
        """
        self.params = {}
        if self.path.find('?') != -1:
            self.path, qs = self.path.split("?", 1)
            for pair in qs.split("&"):
                key, value = pair.split("=")
                self.params[key] = value
        if self.command == "POST":
            clength = int(self.headers.dict['content-length'])
            content = self.rfile.read(clength)
            for pair in content.split("&"):
                key, value = pair.split("=")
                self.params[key] = urllib.unquote_plus(value)
if __name__ == "__main__":
    #init_params( )
    if START_SSL == True:
       print time.asctime(), "Server Starts - %s:%s" % (HTTP_IP, HTTP_PORT)
       try:
           httpd = BaseHTTPServer.HTTPServer((HTTP_IP, HTTP_PORT), MyHandler)
           httpd.socket = ssl.wrap_socket (httpd.socket, server_side=True, certfile=SSL_CERT)
           httpd.serve_forever()
       except KeyboardInterrupt:
           pass
       httpd.server_close()
       print time.asctime(), "Server Stops - %s:%s" % (HTTP_IP, HTTP_PORT)
    else:
       print time.asctime(), "Server Starts - %s:%s" % (HTTP_IP, HTTP_PORT)
       try:
           httpd = BaseHTTPServer.HTTPServer((HTTP_IP, HTTP_PORT), MyHandler)
           httpd.serve_forever()
       except KeyboardInterrupt:
           pass
       httpd.server_close()
       print time.asctime(), "Server Stops - %s:%s" % (HTTP_IP, HTTP_PORT)

