"""A client for the PeerIndex API."""

from datetime import datetime, timedelta
from json import loads
import time

from httplib2 import Http


class PeerIndexError(Exception):
    """Raise if an error occurs while interacting with the PeerIndex API."""


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
    """

    errors = {'Rate limit exceeded': RateLimitError,
              'Invalid API key': CredentialsError}

    def __init__(self, key, client=None):
        self._key = key
        self._client = client or Http()
        self._lastCallTime = None

    def get(self, name):
        """Get the PeerIndex profile for a Twitter user.

        The PeerIndex API has a rate limit of 1 call per second and a maximum
        of 10000 calls per day.  This method will invoke C{time.sleep} to
        ensure the per second limit isn't exceeded.

        @param name: The screen name of the Twitter user.
        @raise RateLimitError: Raised if the rate limit has been exceeded.
        @raise CredentialsError: Raised if an invalid API key is used.
        @raise PeerIndexError: Raised for any other type of error.
        @return: A C{dict} representing data about the user.  See the L{API
            docs<http://dev.peerindex.com/docs/profile/show>} for information
            about the returned keys.
        """
        # if self._lastCallTime:
        #     delta = self._lastCallTime - datetime.utcnow()
        #     if delta < timedelta(seconds=1):
        #         time.sleep(delta.seconds)
        uri = ('http://api.peerindex.net/1/profile/show.json?'
               'id=%s&api_key=%s' % (name, self._key))
        response, contents = self._client.request(uri)
        if response['status'] == '400':
            message = loads(contents)['error']
            exceptionClass = self.errors.get(message, PeerIndexError)
            raise exceptionClass(message)
        elif response['status'] == '404':
            raise UnknownUserError(name)
        else:
            return loads(contents)
