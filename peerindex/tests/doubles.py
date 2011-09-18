from httplib2 import DEFAULT_MAX_REDIRECTS


class FakeHTTPResponse(object):
    """A fake HTTP response that can return a predetermined result."""

    def __init__(self, uri, method, body, headers, redirections,
                 connection_type):
        self.uri = uri
        self.method = method
        self.body = body
        self.headers = headers
        self.redirections = redirections
        self.connection_type = connection_type
        self.response = None

    def result(self, headers, content):
        """Set the response headers and content to return with this response.

        @param headers: A C{dict}-like object containing the HTTP response
            headers to return for this response.
        @param content: The plaintext content to return for this response.
        """
        self.response = (headers, content)


class FakeHTTPClient(object):
    """A fake HTTP client that can be used in place of C{httplib2.Http}."""

    def __init__(self):
        self._responses = []

    def expect(self, uri, method='GET', body=None, headers=None,
               redirections=DEFAULT_MAX_REDIRECTS, connection_type=None):
        """
        Specify the values that expected when the L{request} method is called.
        """
        response = FakeHTTPResponse(uri, method, body, headers, redirections,
                                    connection_type)
        self._responses.append(response)
        return response

    def request(self, uri, method='GET', body=None, headers=None,
                redirections=DEFAULT_MAX_REDIRECTS, connection_type=None):
        """A fake implementation of C{httplib2.Http.request}."""
        response = self._responses.pop(0)
        assert(response.uri == uri, uri)
        assert(response.method == method)
        assert(response.body == body)
        assert(response.headers == headers)
        assert(response.redirections == redirections)
        assert(response.connection_type == connection_type)
        return response.response


class FakeTimeModule(object):
    """A fake C{time} module.

    @param currentTime: Optionally, the current time.  Defaults to 100.0.
    """

    def __init__(self, currentTime=None):
        self.currentTime = currentTime or 100.0
        self.lastSleep = None

    def sleep(self, seconds):
        """Sleep for the specified number of seconds."""
        self.lastSleep = seconds
        self.currentTime += seconds

    def time(self):
        """Get the current time."""
        return self.currentTime
