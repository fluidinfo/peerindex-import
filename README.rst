Importing PeerIndex data to Fluidinfo
------------------------------------

The file `import.py` reads Twitter screen names from stdin, looks up their
PeerIndex data using their API, and adds it to Fluidinfo.

For each screen name, we put the following into Fluidinfo onto the object
whose about tag is the screenname in lowercase, preceeded by an @ sign:

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

The peerindex.com/updated-at tag is a (float) number of seconds from the
epoch and records the time at which we added the data to Fluidinfo.

The other peerindex.com tags have values that are identical to the values
coming back from the PeerIndex API.

To install
----------

Create a virtualenv and install the requirements:

.. code-block:: sh

    $ virtualenv --no-site-packages env
    $ . env/bin/activate
    $ pip install -r requirements.txt

To run
------

You will need the `peerindex.com` user's password and a valid PeerIndex API
key.  Put these in the environment variables FLUIDINFO_PEERINDEX_PASSWORD
and PEERINDEX_API_KEY. Ask Terry for the values.

Note that PeerIndex limit API usage to one call per second and 10K calls
per day.  More details at http://dev.peerindex.com/
