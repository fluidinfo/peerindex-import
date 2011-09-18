from json import dumps
from unittest import TestCase

from peerindex.client import (
    PeerIndex, CredentialsError, RateLimitError, UnknownUserError)
from peerindex.tests.doubles import FakeHTTPClient


class PeerIndexTest(TestCase):

    def testGet(self):
        """
        L{PeerIndex.get} returns a C{dict} with information about the
        specified Twitter user.
        """
        client = FakeHTTPClient()
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=terrycojones&api_key=key')
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
        response.result(headers, content)
        peerindex = PeerIndex('key', client)
        self.assertEqual(result, peerindex.get('terrycojones'))

    def testGetWithBadCredentials(self):
        """
        L{PeerIndex.get} raises a L{CredentialsError} if an invalid API key is
        used.
        """
        client = FakeHTTPClient()
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=terrycojones&api_key=bad-api-key')
        headers = {'status': '400', 'transfer-encoding': 'chunked',
                   'server': 'nginx/0.7.65', 'connection': 'keep-alive',
                   'date': 'Sun, 18 Sep 2011 13:06:03 GMT',
                   'content-type': 'application/json'}
        content = dumps({'error': 'Invalid API key'})
        response.result(headers, content)
        peerindex = PeerIndex('bad-api-key', client)
        self.assertRaises(CredentialsError, peerindex.get, 'terrycojones')

    def testGetWithRateLimitExceeded(self):
        """
        L{PeerIndex.get} raises a L{RateLimitError} if the daily rate limit
        has been reached.
        """
        client = FakeHTTPClient()
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=terrycojones&api_key=key')
        headers = {'status': '400', 'transfer-encoding': 'chunked',
                   'server': 'nginx/0.7.65', 'connection': 'keep-alive',
                   'date': 'Sun, 18 Sep 2011 13:06:03 GMT',
                   'content-type': 'application/json'}
        content = dumps({'error': 'Rate limit exceeded'})
        response.result(headers, content)
        peerindex = PeerIndex('key', client)
        self.assertRaises(RateLimitError, peerindex.get, 'terrycojones')

    def testGetWithUnknownUser(self):
        """
        L{PeerIndex.get} raises a L{UnknownUserError} if the PeerIndex API
        doesn't have information about the specified user.
        """
        client = FakeHTTPClient()
        response = client.expect(
            'http://api.peerindex.net/1/profile/show.json?'
            'id=unknown&api_key=key')
        headers = {'status': '404', 'x-ratelimit-remaining': '9999',
                   '-content-encoding': 'gzip', 'transfer-encoding': 'chunked',
                   'content-length': '2', 'server': 'nginx/0.7.65',
                   'connection': 'keep-alive', 'x-ratelimit-limit': '10000',
                   'date': 'Sun, 18 Sep 2011 14:20:51 GMT',
                   'content-type': 'application/json',
                   'x-ratelimit-reset': '1316386800'}
        content = dumps([])
        response.result(headers, content)
        peerindex = PeerIndex('key', client)
        self.assertRaises(UnknownUserError, peerindex.get, 'unknown')
