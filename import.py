#!/usr/bin/env python

from datetime import datetime
import json
import os
import sys
import time
import urllib

from fom.session import Fluid
from fom.errors import FluidError


if __name__ == '__main__':
    password = os.environ['FLUIDINFO_PEERINDEX_PASSWORD']
    assert password, 'Please set FLUIDINFO_PEERINDEX_PASSWORD in your env.'
    apikey = os.environ['PEERINDEX_API_KEY']
    assert apikey, 'Please set PEERINDEX_API_KEY in your env.'

    fdb = Fluid()
    fdb.login('peerindex.com', password)
    totalTime = 0.0
    screennames = sys.stdin.readlines()
    assert len(screennames) <= 10000, 'Too many input lines (max is 10,000).'

    for i, screenname in enumerate(s[:-1].lower() for s in screennames):
        start = time.time()
        try:
            request = urllib.urlopen(
                'http://api.peerindex.net/1/profile/show.json?id=%s&api_key=%s'
                % (screenname, apikey))
        except IOError, e:
            print >>sys.stderr, 'IOError for %r (%s)' % (screenname, e)
            time.sleep(1.0)
            continue
        data = request.read()
        if not data:
            print >>sys.stderr, 'No data returned for %r' % screenname
            time.sleep(1.0)
            continue
        info = json.loads(data)
        if 'error' in info:
            print >>sys.stderr, 'Error for %r: %r' % (
                screenname, info['error'])
            time.sleep(1.0)
            continue
        updatedAt = time.mktime(datetime.utcnow().timetuple())
        about = '@%s' % screenname.lower()
        response = fdb.objects.post(about=about)
        objectId = response.value['id']
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
            fdb.values.put(query='fluiddb/id="%s"' % objectId, values=values)
        except FluidError, e:
            print 'Error processing %s' % screenname
            print e.args[0].response
            raise
        else:
            elapsed = time.time() - start
            totalTime += elapsed
            print 'Processed %d: %s (%.3f)' % (i + 1, screenname, elapsed)
            # Sleep (if needed) to make sure 1 second has passed since the
            # start of processing so as not to call the PeerIndex API too
            # often.
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
    av = totalTime / (i + 1)
    print 'Average time per user: %.3f' % av
