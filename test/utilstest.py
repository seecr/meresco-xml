## begin license ##
# 
# "Meresco-Xml" is a set of components and tools for handling xml data objects. 
# 
# Copyright (C) 2011 Seecr (Seek You Too B.V.) http://seecr.nl
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
