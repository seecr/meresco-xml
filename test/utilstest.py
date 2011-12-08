
from cq2utils import CQ2TestCase

from meresco.xml.utils import sortRootTagAttrib

class UtilsTest(CQ2TestCase):
    def testSortRootTagAttrib(self):
        input = """<a:root xmlns:b="namespace B" xmlns:a="namespace A">
    <b:sub>tag</b:sub>
</a:root>"""
        self.assertEquals("""<a:root xmlns:a="namespace A" xmlns:b="namespace B">
    <b:sub>tag</b:sub>
</a:root>""", sortRootTagAttrib(input))
