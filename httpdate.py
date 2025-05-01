#!/usr/bin/env python

# Copyright (c) 2017,2019,2020,2025 Mikolaj Kucharski <mikolaj@kucharski.name>
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

from __future__ import print_function

import multiprocessing
import time
import sys

from datetime import datetime, timezone

try:
    from httplib import HTTPConnection
except ImportError:
    from http.client import HTTPConnection
from subprocess import Popen, PIPE


def http_time(ret):
    conn = HTTPConnection("www.google.com", timeout=30)
    conn.request("HEAD", "/")
    res = conn.getresponse()

    if res.status not in [200, 301, 302, 303, 307, 308]:
        raise Exception("Wrong HTTP status code: {}".format(res.status))

    for name, dh in res.getheaders():
        if name.lower() != "date":
            continue
        if not dh.endswith(" GMT"):
            raise Exception("Date not in GMT timezone")

        print("Time from HTTP header is {}".format(dh))
        dt = datetime.strptime(dh, "%a, %d %b %Y %H:%M:%S GMT")
        dt = dt.replace(tzinfo=timezone.utc)

        # current time
        ct = datetime.utcnow().replace(microsecond=0)
        ct = ct.replace(tzinfo=timezone.utc)

        print("Remote datetime is {}".format(dt))
        print("Local datatime is {}".format(ct))

        delta = int(round(abs((ct - dt).total_seconds())))

        print("Timedelta is {} seconds".format(delta))

        if delta < 60 * 10:  # minutes
            ret.value = 0
            return

        nt = "@" + str(int(dt.timestamp()))
        cmd = ["date", "-u", "-s", nt]
        print("Executing command {}".format(" ".join(cmd)))
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdoutdata, stderrdata = p.communicate()

        print("stdout={}".format(stdoutdata.decode("utf-8").strip()))
        print("stderr={}".format(stderrdata.decode("utf-8").strip()))
        print("code={}".format(p.returncode))

        # Command date from BusyBox when fails to set the time
        # prints error on stderr and returns zero exit code. Fail
        # the run, if stderr is not empty.
        if len(stderrdata) > 0:
            print("Command has non-empty stderr!")
            ret.value = 101
            return

        ret.value = 0 if p.returncode == 0 else 101


def get_time():
    manager = multiprocessing.Manager()
    ret_val = manager.Value("i", 100)

    proc = multiprocessing.Process(target=http_time, args=(ret_val,))
    proc.start()

    for _ in range(90):
        if not proc.is_alive():
            break
        time.sleep(1)

    if proc.is_alive():
        print("Terminating {}".format(proc.name), file=sys.stderr)
        proc.terminate()

    proc.join()

    return ret_val.value


def main():
    for num in range(10):
        ret = get_time()
        if ret == 0:
            return 0
        print("Failed unexpectedly with exit code {}".format(ret), file=sys.stderr)
        if ret == 101:
            print("Unrecoverable error, exiting.", file=sys.stderr)
            return 101
        print("Sleeping for {} seconds...".format(2**num), file=sys.stderr)
        time.sleep(2**num)

    print("Unable to finish operation successfully", file=sys.stderr)
    return 50


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
