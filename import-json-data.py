#!/usr/bin/env python

# See README.markdown for usage instructions.

from datetime import datetime
import json
import os
import sys
import time

from fom.session import Fluid
from fom.errors import FluidError


if __name__ == '__main__':
    password = os.environ['FLUIDINFO_PEERINDEX_PASSWORD']
    assert password, 'Please set FLUIDINFO_PEERINDEX_PASSWORD in your env.'
    fdb = Fluid()
    fdb.login('peerindex.com', password)
    totalTime = 0.0

    for i, line in enumerate(sys.stdin.readlines()):
        start = time.time()
        info = json.loads(line[:-1])
        screenname = info['twitter']
        updatedAt = time.mktime(datetime.utcnow().timetuple())
        about = '@%s' % screenname.lower()
        values = {
            'peerindex.com/updated-at': {'value': updatedAt},
            }
        for var in ('activity', 'audience', 'authority', 'peerindex',
                    'realness', 'name', 'slug', 'url', 'topics'):
            try:
                values['peerindex.com/%s' % var] = {'value': info[var]}
            except KeyError:
                pass
        try:
            fdb.values.put(query='fluiddb/about="%s"' % about, values=values)
        except FluidError, e:
            print 'Error processing %s' % screenname
            print e.args[0].response
            raise
        else:
            elapsed = time.time() - start
            totalTime += elapsed
            print 'Processed %d: %s (%.3f)' % (i + 1, screenname, elapsed)
    av = totalTime / (i + 1)
    print 'Average time per user: %.3f' % av
