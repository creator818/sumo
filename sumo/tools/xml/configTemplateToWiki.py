#!/usr/bin/env python
"""
@file    configTemplateToWiki.py
@author  Michael Behrisch
@version $Id$

Generate Wiki table from configuration template.

SUMO, Simulation of Urban MObility; see http://sumo-sim.org/
Copyright (C) 2008-2013 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""
import sys
from xml.sax import parse, handler

class ConfigReader(handler.ContentHandler):

    def __init__(self, mergeWikiTxt):
        self._level = 0
        self._mergeWiki = mergeWikiTxt
        self._intro = {}
        self._end = len(mergeWikiTxt)
        active = False
        currSect = ""
        for idx, line in enumerate(mergeWikiTxt):
            line = line.strip('\n\r')
            if line == "==Options==":
                active = True
            if active:
                if line[:3] == "===":
                    start = idx
                    currSect = line
                elif line[:2] == "{|":
                    self._intro[currSect] = (start, idx)
                elif line[:4] == "----" or line[:2] == "=S":
                    self._end = idx
                    break
            if currSect == "":
                print line

    def startElement(self, name, attrs):
        if self._level == 1:
            # subtopic
            title = "===%s===" % name.replace("_", " ").title()
            if title in self._intro:
                begin, end = self._intro[title]
                title = ("".join(self._mergeWiki[begin:end])).strip()
            print """%s
{| cellspacing="0" border="1" width="90%%" align="center"
|-
! style="background:#ddffdd;" valign="top" | Option
! style="background:#ddffdd;" valign="top" | Description""" % title
        if self._level == 2:
            # entry
            print '|-\n| valign="top" |',
            a = ""
            for s in attrs.get('synonymes', '').split():
                if len(s) == 1:
                    a = s
            if a != "":
                print '{{Option|-%s {{DT_%s}}}}<br/>' % (a, attrs['type']),
            print '{{Option|--%s {{DT_%s}}}}' % (name, attrs['type'])
            suffix = ""
            if attrs['value']:
                suffix = "; ''default: %s''" % attrs['value']
            print '| valign="top" | %s%s' % (attrs['help'], suffix)
        self._level += 1

    def endElement(self, name):
        self._level -= 1
        if self._level == 1:
            # subtopic end
            print "|-\n|}\n"

    def endDocument(self):
        print ("".join(self._mergeWiki[self._end:])).strip()

if __name__ == "__main__":
    parse(sys.argv[1], ConfigReader(open(sys.argv[2]).readlines()))
