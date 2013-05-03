#!/bin/bash
## begin license ##
#
# "Meresco-Xml" is a set of components and tools for handling xml data objects.
#
# Copyright (C) 2010 Seek You Too (CQ2) http://www.cq2.nl
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

set -o errexit
rm -rf tmp build
mydir=$(cd $(dirname $0); pwd)
source /usr/share/seecr-test/functions

pyversions="2.6"
if distro_is_debian_wheezy; then
    pyversions="2.6 2.7"
fi

VERSION="x.y.z"

for pyversion in $pyversions; do
    definePythonVars $pyversion
    echo "###### $pyversion, $PYTHON"
    ${PYTHON} setup.py install --root tmp
done
cp -r test tmp/test
removeDoNotDistribute tmp
find tmp -name '*.py' -exec sed -r -e "
    s/\\\$Version:[^\\\$]*\\\$/\\\$Version: ${VERSION}\\\$/;
    " -i '{}' \;

cp -r test tmp/test
runtests "$@"
rm -rf tmp build

