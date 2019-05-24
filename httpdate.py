#!/usr/bin/env python2

# Copyright (c) 2017 Mikolaj Kucharski <mikolaj@kucharski.name>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from datetime import datetime
from httplib import HTTPConnection
from subprocess import Popen, PIPE
from sys import exit

def main():
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
		dt = datetime.strptime(dh, '%a, %d %b %Y %H:%M:%S %Z')

		# current time
		ct = datetime.utcnow().replace(microsecond=0)

		print("Remote datetime is %s" % str(dt))
		print("Local datatime is %s" % str(ct))

		delta = ct - dt
		delta = abs(delta.total_seconds())

		print("Timedelta is %d seconds" % delta)

		if delta < 60 * 10:	# minutes
			exit(0)

		nt = dt.strftime('%Y%m%d%H%M.%S')
		cmd = ['date', '-u', '-s', nt]
		print("Executing command %s" % ' '.join(cmd))
		p = Popen(cmd, stdout=PIPE, stderr=PIPE)
		stdoutdata, stderrdata = p.communicate()

		print("stdout=%s" % stdoutdata.strip())
		print("stderr=%s" % stderrdata.strip())
		print("code=%d" % p.returncode)

		exit(p.returncode)

if __name__ == '__main__':
    main()
