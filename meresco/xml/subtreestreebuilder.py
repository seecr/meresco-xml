## begin license ##
#
# "Meresco-Xml" is a set of components and tools for handling xml data objects.
#
# Copyright (C) 2013, 2020 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Meresco-Xml"
#
# "Meresco-Xml" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco-Xml" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco-Xml"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from lxml.etree import TreeBuilder, XMLParser, parse, tostring

from os.path import abspath, dirname, join


class SubTreesTreeBuilder(object):
    def __init__(self, buildFor=None, elementPath=None, treeBuilderFactory=TreeBuilder, onResult=None):
        if elementPath:
            buildFor = {elementPath[-1]: lambda stack: [d['tag'] for d in stack] == elementPath}
        self._buildFor = buildFor
        self._treeBuilderFactory = treeBuilderFactory
        self._onResult = onResult
        self._subtrees = []
        self._currentTreeBuilders = {}
        self._stack = []

    def buildFor(self):
        return [id for (id, f) in list(self._buildFor.items()) if f(self._stack)]

    def _nsmapFullStack(self):
        enrichedNSmap = {}
        for node in self._stack:
            enrichedNSmap.update(node['nsmap'])
        return enrichedNSmap

    def getSubtrees(self):
        # *Must* be called after XMLParser.close() too!
        while self._subtrees:
            yield self._subtrees.pop(0)

    # etree TreeBuilder interface
    def start(self, tag, attrs, nsmap=None):
        if nsmap is None:
            nsmap = {}
        self._stack.append({'tag': tag, 'attrs': attrs, 'nsmap': nsmap})

        for tb in list(self._currentTreeBuilders.values()):
            tb.start(tag, attrs, nsmap)

        builders = self.buildFor()
        if builders:
            for id in builders:
                builder = self._treeBuilderFactory()
                namespaces = self._nsmapFullStack()
                builder.start(tag, attrs, namespaces)
                self._currentTreeBuilders[id] = builder

    def comment(self, comment):
        for tb in list(self._currentTreeBuilders.values()):
            tb.comment(comment)

    def data(self, data):
        for tb in list(self._currentTreeBuilders.values()):
            tb.data(data)

    def end(self, tag):
        builders = self.buildFor()
        assert self._stack.pop()['tag'] == tag, 'Stack and parser out-of-sync.'

        if not self._currentTreeBuilders:
            return

        for tb in list(self._currentTreeBuilders.values()):
            tb.end(tag)

        if builders:
            for id in builders:
                root = self._currentTreeBuilders[id].close()
                if self._onResult:
                    self._onResult(root)
                self._subtrees.append((id, root))
                del self._currentTreeBuilders[id]

    def pi(self, target, data):
        for tb in list(self._currentTreeBuilders.values()):
            tb.pi(target, data)

    def close(self):
        assert not self._currentTreeBuilders, 'TreeBuilder(s) still present on close.'


class SimpleSaxFileParser(object):
    def __init__(self, stream, path, callback):
        self._stream = stream
        self._path = path
        self._callback = callback

    def start(self):
        def isPath(stack):
            return [d['tag'] for d in stack] == self._path
        builder = SubTreesTreeBuilder(buildFor={
            'simple': isPath,
        })
        def processSubtrees():
            for id, subtree in builder.getSubtrees():
                self._callback(subtree)
        parser = XMLParser(target=builder)

        data = self._stream.read(4096)
        while data:
            parser.feed(data)
            processSubtrees()
            data = self._stream.read(4096)
        parser.close()
        processSubtrees()

