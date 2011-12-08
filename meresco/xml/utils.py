
def sortRootTagAttrib(xmlString):
    root, remainder = xmlString.split(">", 1)
    rootAttribs = root[root.find(' '):].strip()

    def nextAtrrib(text):
        pos = 0
        while True:
            newPos = text.find('"', pos)
            if newPos == -1:
                return
            newPos = text.find('"', newPos+1)
            if newPos == -1:
                return
            yield text[pos:newPos + 1]
            pos = newPos + 2

    newXmlString = root[:root.find(' ') + 1]
    newXmlString += ' '.join(sorted(list(nextAtrrib(rootAttribs))))
    newXmlString += '>'
    newXmlString += remainder
    return newXmlString

