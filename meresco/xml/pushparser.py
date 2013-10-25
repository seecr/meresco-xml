from lxml.etree import XMLParser

from meresco.xml.subtreestreebuilder import SubTreesTreeBuilder


class PushParser(object):
    def __init__(self, elementPath, onResultDo):
        builder = SubTreesTreeBuilder(elementPath=elementPath, onResult=onResultDo)
        self._parser = XMLParser(target=builder)

    def feed(self, data):
        self._parser.feed(data)

