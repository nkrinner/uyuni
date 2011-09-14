#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Novell, Inc.
#   This library is free software; you can redistribute it and/or modify
# it only under the terms of version 2.1 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
#
#   This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
#   You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import unittest2 as unittest
from StringIO import StringIO

from mock import Mock, patch

from susemanager import mgr_ncc_sync_lib as ncc_sync

class SyncTest(unittest.TestCase):
    def setUp(self):
        ncc_sync.initCFG = ncc_sync.CFG = Mock()
        ncc_sync.rhnSQL.initDB = Mock()
        ncc_sync.rhnLog.initLOG = Mock()
        ncc_sync.suseLib.getProductProfile = Mock(return_value=
                                                  {"guid":"bogus_guid"})
        self.sync = ncc_sync.NCCSync()

    def tearDown(self):
        del(self.sync)

    def test_get_ncc_xml_expat_error(self):
        # pylint: disable=W0404
        from xml.parsers.expat import ExpatError
        ncc_sync.rhnLog.LOG = Mock()
        ncc_sync.rhnLog.LOG.file = "logfile.log"

        ncc_sync.suseLib.send = Mock(return_value=StringIO("<xml>is invalid"))

        myerr = StringIO()
        with patch("sys.stderr", myerr):
            self.assertRaises(SystemExit, self.sync._get_ncc_xml, "some_url")
        myerr.seek(0)
        err = myerr.read()
        self.assertIn("Could not parse XML from some_url. The remote document "
                      "does not appear to be a valid XML document. This "
                      "document was written to the logfile: logfile.log.", err)
        self.assertIn("Invalid XML document (got ExpatError) from some_url: "
                      "<xml>is invalid", err)

    def test_get_ncc_xml_valid_xml(self):
        # pylint: disable=W0404
        from xml.etree.ElementTree import Element
        ncc_sync.suseLib.send = Mock(return_value=StringIO("<xml>valid</xml>"))

        self.assertEqual(self.sync._get_ncc_xml("some_url").text, "valid")
