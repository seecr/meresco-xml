## begin license ##
#
# "Meresco-Xml" is a set of components and tools for handling xml data objects.
#
# Copyright (C) 2005-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2013 Seecr (Seek You Too B.V.) http://seecr.nl
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

from unittest import TestCase
from meresco.xml.normalize import Normalize

"""
regexp: http://docs.python.org/lib/re-syntax.html
string format: http://docs.python.org/lib/typesseq-strings.html
"""

class NormalizeTest(TestCase):

	def testOne(self):
		from re import compile
		inValue    = '2006-11-28 19:00'
		outValue = '2006-11-28T19:00'
		rule = (r'(\d{2,4}-\d{2}-\d{2}) (\d{2}:\d{2})', '%sT%s')
		normalizer = lambda x: rule[1] % (compile(rule[0]).match(x).groups())
		self.assertEqual( outValue, normalizer(inValue))

	def testNormalizeOneRule(self):
		rules = [(r'(\d{2,4}-\d{2}-\d{2}) (\d{2}:\d{2})', '%sT%s')]
		normalize = Normalize(rules)
		result = normalize.process('2006-11-28 19:00')
		self.assertEqual('2006-11-28T19:00', result)

	def testTwoRules(self):
		rules = [('aap (.*)', '%s'), ('noot (.*)', '%s')]
		normalize = Normalize(rules)
		r1 = normalize.process('aap noot mies')
		self.assertEqual('noot mies', r1)
		r2 = normalize.process('noot aap boom')
		self.assertEqual('aap boom', r2)

	def testRuleWithCustomProcessing(self):
		class Lower:
			def __init__(self, string):
				self.string = string
			def __mod__(self, values):
				return self.string % tuple(value.lower() for value in values)
		rules = [('b(OO)m', Lower('%s'))]
		normalize = Normalize(rules)
		r1 = normalize.process('bOOm')
		self.assertEqual('oo', r1)

	def testRuleWithPostProcessing(self):
		rules = [('b(OO)m v(uu)r v(.*)s', '%s %s %s', (str.lower, str.upper, str.strip))]
		normalize = Normalize(rules)
		r1 = normalize.process('bOOm vuur v   ii   s')
		self.assertEqual('oo UU ii', r1)

