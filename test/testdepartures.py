# -*- coding: utf-8 -*-
import unittest
from departures import HslRequests

buses_1576 = [u'2321  2:Elielinaukio, l. 24',
              u'2321N 2:Elielinaukio, l. 24',
              u'2345  2:Elielinaukio, l. 23',
              u'2345N 2:Elielinaukio, l. 23',
              u'4322  2:Elielinaukio, l. 24',
              u'4332  2:Elielinaukio, l. 23',
              u'7346  2:Linja-autoas., l. 18',
              u'7355  2:L.-autoas., l. 14',
              u'7355T 2:L-autoas., l. 14']


class DeparturesTests(unittest.TestCase):
    def setUp(self):
        f = open("keys.keys")
        lines = f.readlines()
        f.close()
        self.username = lines[1].strip()
        self.password = lines[2].strip()

    def test_1572(self):
        h = HslRequests(self.username, self.password)
        s = h.stop_summary(1572)
        self.assertIn("1572", s)

    def test_unexisting(self):
        h = HslRequests(self.username, self.password)
        s = h.stop_summary(1232131)
        self.assertIn("ei löydy pysäkki", s)


    def test_summary_line(self):
        h = HslRequests(self.username, self.password)
        s = h.stop_lines_summary(1576)
        self.assertIn("1576", s)
        self.assertIn("elielinaukio", s)


if __name__ == '__main__':
    unittest.main()
