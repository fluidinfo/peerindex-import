"""A client for the PeerIndex API.

The PeerIndex API has a single C{profile/show} method to get information about
a particular Twitter user::

  peerindex = PeerIndex('your-api-key')
  result = peerindex.get('twitter-user')

The C{dict} returned by this method includes the keys described here:

  http://dev.peerindex.com/docs/profile/show

The PeerIndex API has a one call per second rate limit.  Calls to
L{PeerIndex.get} will sleep to ensure this limit is honoured.
"""

from json import loads
import time

from httplib2 import Http


class PeerIndexError(Exception):
    """Raised if an error occurs while interacting with the PeerIndex API."""


class CredentialsError(PeerIndexError):
    """Raised if bad credentials are used."""


class RateLimitError(PeerIndexError):
    """Raised if the daily rate limit is reached."""


class UnknownUserError(PeerIndexError):
    """Raised if a request for an unknown user is made."""


class PeerIndex(object):
    """A client for the PeerIndex API.

    @param key: The API key to use when making requests to PeerIndex.
    @param client: Optionally, an C{httplib2.Http}-compatible object.  It's
        used for testing purposes.
    @param timeModule: Optionally, a C{time}-compatible module object.  It's
        used for testing purposes.
    """

    errors = {'Rate limit exceeded': RateLimitError,
              'Invalid API key': CredentialsError}

    def __init__(self, key, client=None, timeModule=None):
        self._key = key
        self._client = client or Http()
        self._timeModule = timeModule or time
        self._lastCallTime = None

    def get(self, name):
        """Get the PeerIndex profile for a Twitter user.

        The PeerIndex API has a rate limit of one call per second and a
        maximum of 10000 calls per day.  This method will invoke C{time.sleep}
        to ensure the per second limit isn't exceeded.

        @param name: The screen name of the Twitter user.
        @raise RateLimitError: Raised if the rate limit has been exceeded.
        @raise CredentialsError: Raised if an invalid API key is used.
        @raise UnknownUserError: Raised if information about the specified
            Twitter user isn't available.
        @raise PeerIndexError: Raised for any other type of error.
        @return: A C{dict} representing data about the user.  See the L{API
            docs<http://dev.peerindex.com/docs/profile/show>} for information
            about the returned keys.
        """
        name = name.strip()
        if name.startswith('@'):
            name = name[1:]

        self._limitCallRate()
        uri = ('http://api.peerindex.net/1/profile/show.json?'
               'id=%s&api_key=%s' % (name, self._key))
        headers, contents = self._client.request(uri)
        if headers['status'] == '400' or headers['status'] == '403':
            message = loads(contents)['error']
            exceptionClass = self.errors.get(message, PeerIndexError)
            raise exceptionClass(message)
        elif headers['status'] == '404' or '404 Not Found' in contents:
            raise UnknownUserError(name)
        elif headers['status'] != '200':
            raise PeerIndexError('%s: %s' % (headers, contents))
        else:
            return loads(contents)

    def _limitCallRate(self):
        """Ensure we don't exceed one call per second.

        If this is the first API call, nothing is done, otherwise, a sleep
        will be performed to ensure we don't exceed the one call per second
        rate limit.
        """
        if self._lastCallTime is not None:
            delta = self._timeModule.time() - self._lastCallTime
            if delta < 1.0:
                self._timeModule.sleep(1.0 - delta)
        self._lastCallTime = self._timeModule.time()
