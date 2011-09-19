Importing PeerIndex data to Fluidinfo
=====================================

Fetching and importing from the PeerIndex API
---------------------------------------------

The file `import.py` reads Twitter screen names from stdin, looks up their
PeerIndex data using their API, and adds it to Fluidinfo.

For each screen name, we put the following into Fluidinfo onto the object
whose about tag is the screenname in lowercase, preceeded by an `@` sign:

<pre>
  peerindex.com/updated-at
  peerindex.com/activity
  peerindex.com/audience
  peerindex.com/authority
  peerindex.com/peerindex
  peerindex.com/realness
  peerindex.com/name
  peerindex.com/slug
  peerindex.com/url
  peerindex.com/topics
</pre>

The peerindex.com/updated-at tag is a (float) number of seconds from the
epoch and records the time at which we added the data to Fluidinfo.

The other peerindex.com tags have values that are identical to the values
coming back from the PeerIndex API.

Importing already fetched JSON data
-----------------------------------

The `import-json-data.py` script reads lines from `stdin` that each contain the JSON
output of a call to the PeerIndex API. Input data of that type is produced by the
download script written by Jamu Kakar (which will be merged to this repo shortly).

To install
----------

Create a virtualenv and install the requirements:

<pre>
  $ virtualenv --no-site-packages env
  $ . env/bin/activate
  $ pip install -r requirements.txt
</pre>

To run
------

You will need the `peerindex.com` user's password. Put this in the
environment variable `FLUIDINFO_PEERINDEX_PASSWORD`.

For `import.py` (which makes API calls to PeerIndex), you will also need to
set the environment variable `PEERINDEX_API_KEY` to a valid PeerIndex API.
Ask Terry for his if you don't have one.  Note that PeerIndex limit API
usage to one call per second and 10K calls per day.  More details at
`http://dev.peerindex.com/`
