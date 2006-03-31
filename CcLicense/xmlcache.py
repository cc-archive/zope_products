"""
CcLicense
xmlcache.py
$Id$

copyright 2004-2005, Nathan R. Yergler, Creative Commons
licensed to the public under the GNU GPL 2
"""

import os
import lxml.etree

class XmlCache(object):
    CHECK_INTERVAL = 10
	
    def __init__(self, filename):
        self.__filename = filename
        self.__count = 0

        self.__loadFile()

    def __loadFile(self):
        self.__doc = lxml.etree.parse(file(self.__filename, 'r'))
        self.__lastMod = self.__modTime()

    def __modTime(self):
        return os.stat(self.__filename).st_mtime

    def __call__(self):
        if self.__count < self.CHECK_INTERVAL:
            self.__count = self.__count + 1
        else:
            self.__count = 0
            if self.__modTime() != self.__lastMod:
                self.__loadFile()

        return self.__doc

