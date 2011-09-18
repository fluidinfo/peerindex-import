from json import dumps
from unittest import TestCase

from peerindex.client import (
    PeerIndex, PeerIndexError, CredentialsError, RateLimitError,
    UnknownUserError)
from peerindex.tests.doubles import FakeHTTPClient, FakeTimeModule


class PeerIndexTest(TestCase):

    def testGet(self):
        """
        L{PeerIndex.get} returns a C{dict} with information about the
        specified Twitter user.
        """
        client = FakeHTTPClient()
        headers = {'status': '200', 'x-ratelimit-remaining': '9998',
                   'content-location': 'http://api.peerindex.net/...',
                   '-content-encoding': 'gzip', 'transfer-encoding': 'chunked',
                   'content-length': '238', 'server': 'nginx/0.7.65',
                   'connection': 'keep-alive', 'x-ratelimit-limit': '10000',
                   'date': 'Sun, 18 Sep 2011 14:25:33 GMT',
                   'content-type': 'application/json',
                   'x-ratelimit-reset': '1316386800'}
        result = {'name': 'Terry Jones', 'twitter': 'terrycojones',
                  'slug': 'terrycojones', 'known': 1, 'authority': 51,
                  'activity': 46, 'audience': 57, 'peerindex': 52,
                  'url': 'http:\\/\\/pi.mu\\/4O9',
                  'topics': ['languages', 'terry jones', 'catalonia',
                             'tim oreilly', 'writing']}
        content = dumps(result)
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=terrycojones&api_key=key')
        response.result(headers, content)
        peerindex = PeerIndex('key', client=client)
        self.assertEqual(result, peerindex.get('terrycojones'))

    def testGetStripsLeadingAtSignInUsername(self):
        """
        L{PeerIndex.get} automatically strips a leading C{@} sign out of a
        username, since passing it to the API will result in a 404.
        """
        client = FakeHTTPClient()
        headers = {'status': '200', 'x-ratelimit-remaining': '9998',
                   'content-location': 'http://api.peerindex.net/...',
                   '-content-encoding': 'gzip', 'transfer-encoding': 'chunked',
                   'content-length': '238', 'server': 'nginx/0.7.65',
                   'connection': 'keep-alive', 'x-ratelimit-limit': '10000',
                   'date': 'Sun, 18 Sep 2011 14:25:33 GMT',
                   'content-type': 'application/json',
                   'x-ratelimit-reset': '1316386800'}
        result = {'name': 'Terry Jones', 'twitter': 'terrycojones',
                  'slug': 'terrycojones', 'known': 1, 'authority': 51,
                  'activity': 46, 'audience': 57, 'peerindex': 52,
                  'url': 'http:\\/\\/pi.mu\\/4O9',
                  'topics': ['languages', 'terry jones', 'catalonia',
                             'tim oreilly', 'writing']}
        content = dumps(result)
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=terrycojones&api_key=key')
        response.result(headers, content)
        peerindex = PeerIndex('key', client=client)
        self.assertEqual(result, peerindex.get('@terrycojones'))

    def testGetStripsTrailingWhitespaceInUsername(self):
        """
        L{PeerIndex.get} automatically strips trailing whitespace from a
        username, since passing a username with trailing whitespace to the API
        can result in strange behaviour.  For example, at the time of this
        writing, a username with a trailing newline will result in an HTTP 200
        status code with HTML representing a 404 as the response contents.
        """
        client = FakeHTTPClient()
        headers = {'status': '200', 'x-ratelimit-remaining': '9998',
                   'content-location': 'http://api.peerindex.net/...',
                   '-content-encoding': 'gzip', 'transfer-encoding': 'chunked',
                   'content-length': '238', 'server': 'nginx/0.7.65',
                   'connection': 'keep-alive', 'x-ratelimit-limit': '10000',
                   'date': 'Sun, 18 Sep 2011 14:25:33 GMT',
                   'content-type': 'application/json',
                   'x-ratelimit-reset': '1316386800'}
        result = {'name': 'Terry Jones', 'twitter': 'terrycojones',
                  'slug': 'terrycojones', 'known': 1, 'authority': 51,
                  'activity': 46, 'audience': 57, 'peerindex': 52,
                  'url': 'http:\\/\\/pi.mu\\/4O9',
                  'topics': ['languages', 'terry jones', 'catalonia',
                             'tim oreilly', 'writing']}
        content = dumps(result)
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=terrycojones&api_key=key')
        response.result(headers, content)
        peerindex = PeerIndex('key', client=client)
        self.assertEqual(result, peerindex.get('terrycojones\n'))

    def testGetSleepsToHonourRateLimit(self):
        """
        The PeerIndex API limits calls to 1 per second.  L{PeerIndex.get}
        sleeps between calls to ensure this limit is honoured.
        """
        timeModule = FakeTimeModule()
        client = FakeHTTPClient()
        headers = {'status': '200'}
        result = {'name': 'Terry Jones', 'twitter': 'terrycojones',
                  'slug': 'terrycojones', 'known': 1, 'authority': 51,
                  'activity': 46, 'audience': 57, 'peerindex': 52,
                  'url': 'http:\\/\\/pi.mu\\/4O9',
                  'topics': ['languages', 'terry jones', 'catalonia',
                             'tim oreilly', 'writing']}
        content = dumps(result)
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=terrycojones&api_key=key')
        response.result(headers, content)
        peerindex = PeerIndex('key', client=client, timeModule=timeModule)
        self.assertEqual(result, peerindex.get('terrycojones'))
        # No sleep occurs during the first call, because there's no rate
        # limiting to do yet.
        self.assertEqual(None, timeModule.lastSleep)
        self.assertEqual(100.0, peerindex._lastCallTime)

        # Bump the current time by 0.25s to simulate time being spent handling
        # the first request.
        timeModule.currentTime = 100.25
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=terrycojones&api_key=key')
        response.result(headers, content)
        self.assertEqual(result, peerindex.get('terrycojones'))
        # A sleep is performed between calls, with 0.05s of extra time, to
        # ensure that we don't exceed the per-call rate limit.
        self.assertEqual(0.80, timeModule.lastSleep)

    def testGetOnlySleepsWhenNecessary(self):
        """
        L{PeerIndex.get} doesn't sleep if more than one second has passed
        between API calls.
        """
        timeModule = FakeTimeModule()
        client = FakeHTTPClient()
        headers = {'status': '200'}
        result = {'name': 'Terry Jones', 'twitter': 'terrycojones',
                  'slug': 'terrycojones', 'known': 1, 'authority': 51,
                  'activity': 46, 'audience': 57, 'peerindex': 52,
                  'url': 'http:\\/\\/pi.mu\\/4O9',
                  'topics': ['languages', 'terry jones', 'catalonia',
                             'tim oreilly', 'writing']}
        content = dumps(result)
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=terrycojones&api_key=key')
        response.result(headers, content)
        peerindex = PeerIndex('key', client=client, timeModule=timeModule)
        self.assertEqual(result, peerindex.get('terrycojones'))
        # No sleep occurs during the first call, because there's no rate
        # limiting to do yet.
        self.assertEqual(None, timeModule.lastSleep)
        self.assertEqual(100.0, peerindex._lastCallTime)

        # Bump the current time by 5s to simulate time being spent handling
        # the first request.
        timeModule.currentTime = 105.0
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=terrycojones&api_key=key')
        response.result(headers, content)
        self.assertEqual(result, peerindex.get('terrycojones'))
        # No sleep occurs because more than one second has passed since the
        # last API call.
        self.assertEqual(None, timeModule.lastSleep)

    def testGetWithBadCredentials(self):
        """
        L{PeerIndex.get} raises a L{CredentialsError} if an invalid API key is
        used.
        """
        client = FakeHTTPClient()
        headers = {'status': '400', 'transfer-encoding': 'chunked',
                   'server': 'nginx/0.7.65', 'connection': 'keep-alive',
                   'date': 'Sun, 18 Sep 2011 13:06:03 GMT',
                   'content-type': 'application/json'}
        content = dumps({'error': 'Invalid API key'})
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=terrycojones&api_key=bad-api-key')
        response.result(headers, content)
        peerindex = PeerIndex('bad-api-key', client=client)
        self.assertRaises(CredentialsError, peerindex.get, 'terrycojones')

    def testGetWithRateLimitExceeded(self):
        """
        L{PeerIndex.get} raises a L{RateLimitError} if the daily rate limit
        has been reached.
        """
        client = FakeHTTPClient()
        headers = {'status': '400', 'transfer-encoding': 'chunked',
                   'server': 'nginx/0.7.65', 'connection': 'keep-alive',
                   'date': 'Sun, 18 Sep 2011 13:06:03 GMT',
                   'content-type': 'application/json'}
        content = dumps({'error': 'Rate limit exceeded'})
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=terrycojones&api_key=key')
        response.result(headers, content)
        peerindex = PeerIndex('key', client=client)
        self.assertRaises(RateLimitError, peerindex.get, 'terrycojones')

    def testGetWithUnknownUser(self):
        """
        L{PeerIndex.get} raises an L{UnknownUserError} if the PeerIndex API
        doesn't have information about the specified user.
        """
        client = FakeHTTPClient()
        headers = {'status': '404', 'x-ratelimit-remaining': '9999',
                   '-content-encoding': 'gzip', 'transfer-encoding': 'chunked',
                   'content-length': '2', 'server': 'nginx/0.7.65',
                   'connection': 'keep-alive', 'x-ratelimit-limit': '10000',
                   'date': 'Sun, 18 Sep 2011 14:20:51 GMT',
                   'content-type': 'application/json',
                   'x-ratelimit-reset': '1316386800'}
        content = dumps([])
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=unknown&api_key=key')
        response.result(headers, content)
        peerindex = PeerIndex('key', client=client)
        self.assertRaises(UnknownUserError, peerindex.get, 'unknown')

    def testGetWithUnexpectedError(self):
        """
        L{PeerIndex.get} raises a L{PeerIndexError} if an unexpected error
        occurs while using the PeerIndex API.
        """
        client = FakeHTTPClient()
        headers = {'status': '500', 'x-ratelimit-remaining': '9999',
                   '-content-encoding': 'gzip', 'transfer-encoding': 'chunked',
                   'content-length': '2', 'server': 'nginx/0.7.65',
                   'connection': 'keep-alive', 'x-ratelimit-limit': '10000',
                   'date': 'Sun, 18 Sep 2011 14:20:51 GMT',
                   'content-type': 'application/json',
                   'x-ratelimit-reset': '1316386800'}
        content = dumps({'error': 'Something random just happened!'})
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=unknown&api_key=key')
        response.result(headers, content)
        peerindex = PeerIndex('key', client=client)
        self.assertRaises(PeerIndexError, peerindex.get, 'unknown')
