#!/usr/bin/python

# python2.7

from datetime import datetime
from httplib import HTTPConnection
from subprocess import Popen, PIPE
from sys import exit

conn = HTTPConnection("www.google.com")
conn.request("HEAD", "/")
res = conn.getresponse()

if res.status not in [200, 301, 302]:
	raise Exception("Wrong HTTP status code")

for name, dh in res.getheaders():
	if name != 'date':
		continue
	if not dh.endswith(' GMT'):
		raise Exception('Date not in GMT timezone')
	print("Time from HTTP header is %s" % dh)
	# Thu, 29 Dec 2016 19:39:39 GMT
	dt = datetime.strptime(dh, '%a, %d %b %Y %H:%M:%S %Z')

	# current time
	ct = datetime.utcnow()

	print("Remote datetime is %s" % str(dt))
	print("Local datatime is %s" % str(ct))

	delta = ct - dt
	delta = abs(delta.total_seconds())

	print("Timedelta is %f seconds" % delta)

	if delta < 60 * 10:	# minutes
		exit(0)

	# [[[[[YY]YY]MM]DD]hh]mm[.ss]
	# date -u 201612291939.40
	nt = dt.strftime('%Y%m%d%H%M.%S')
	cmd = ['date', '-u', nt]
	print("Executing command %s" % ' '.join(cmd))
	p = Popen(cmd, stdout=PIPE, stderr=PIPE)
	stdoutdata, stderrdata = p.communicate()
	print("stdout=%s" % stdoutdata.strip())
	print("stderr=%s" % stderrdata.strip())
	print("code=%d" % p.returncode)
	exit(p.returncode)
