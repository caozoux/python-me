#!/usr/bin/env python2.7
import re
import sys

class PatchFetchBase(object):

    """Docstring for PatchFetchBase. """

    def __init__(self, remote):
        """TODO: to be defined1. """
        self.remote = remote
    def fetchMerge(self, commit):    
