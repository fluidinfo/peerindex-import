#!/usr/bin/env python

import logging
from json import dumps
import sys

from peerindex.client import PeerIndex, PeerIndexError, RateLimitError


def getProfiles(peerindex, names):
    """Download PeerIndex profiles for the specified Twitter users.

    @param peerindex: The L{PeerIndex} client instance to use.
    @param names: The Twitter users to download profiles for.
    @return: Generator yields profiles for each Twitter user, as they're
        retrieved.
    """
    for name in names:
        for retry in range(3):
            try:
                yield peerindex.get(name)
                logging.info('Retrieved profile for %s' % name)
            except RateLimitError:
                raise
            except PeerIndexError as error:
                logging.exception(error)
            else:
                break
        else:
            logging.warning("Couldn't get a profile for %s" % name)


def main(key, inputPath, outputPath):
    """
    Load Twitter users from the specified file and download PeerIndex
    profiles.

    @param key: The L{PeerIndex} API key to use.
    @param inputPath: The path to the file containing a list of Twitter users,
        one per line.
    @param outputPath: The path to the file to write results to.
    """
    peerindex = PeerIndex(key)
    with open(inputPath, 'r') as inputFile:
        names = [line.strip() for line in inputFile]
    for result in getProfiles(peerindex, names):
        with open(outputPath, 'a') as outputFile:
            print >> outputFile, dumps(result)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit('Need to pass KEY, INPUT_PATH and OUTPUT_PATH arguments.')
    logging.basicConfig(format='%(asctime)s %(levelname)8s  %(message)s',
                        level=logging.INFO)
    key = sys.argv[1]
    inputPath = sys.argv[2]
    outputPath = sys.argv[3]
    main(key, inputPath, outputPath)
