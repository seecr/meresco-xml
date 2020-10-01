## begin license ##
#
# "Meresco-Xml" is a set of components and tools for handling xml data objects.
#
# Copyright (C) 2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2015, 2020 Seecr (Seek You Too B.V.) http://seecr.nl
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

from re import compile as _compile

def compile(rule):
	try:
		return _compile(rule)
	except Exception as e:
		raise Exception(str(e) + ': ' + rule)

class Normalize(object):
	_default = object()
	def __init__(self, rules, noMatchResult=_default):
		self.rules = [(compile(rule[0]),) + rule[1:] for rule in rules]
		self._noMatchResult = noMatchResult

	def process(self, value, noMatchResult=_default):
		for rule in self.rules:
			match = rule[0].match(value)
			if match:
				if len(rule) > 2:
					values = tuple(function(value) for function, value in zip(rule[2], match.groups()))
				else:
					values = match.groups()
				return rule[1] % values
		return self._noResult(noMatchResult, self._noMatchResult, value)

	def _noResult(self, *args):
		for a in args:
			if a is not self._default:
				return a
		return args[-1]