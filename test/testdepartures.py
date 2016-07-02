# -*- coding: utf-8 -*-
import os
import unittest
from unittest import TestCase

from departures import HslRequests, normalize_stopcode

buses_1576 = [u'2321  2:Elielinaukio, l. 24',
              u'2321N 2:Elielinaukio, l. 24',
              u'2345  2:Elielinaukio, l. 23',
              u'2345N 2:Elielinaukio, l. 23',
              u'4322  2:Elielinaukio, l. 24',
              u'4332  2:Elielinaukio, l. 23',
              u'7346  2:Linja-autoas., l. 18',
              u'7355  2:L.-autoas., l. 14',
              u'7355T 2:L-autoas., l. 14']


class DeparturesTests(TestCase):
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
        self.assertIn("has no such", s[0])

    def test_summary_line(self):
        h = HslRequests(self.username, self.password)
        s = h.stop_lines_summary(1576)
        self.assertIn("1576", s)
        self.assertIn("elielinaukio", s.lower())


class LambdaTests(TestCase):
    def test_environment_lambda_name(self):
        self.assertTrue(os.environ.has_key("LAMBDANAME"))

    def test_environment_lambda_url(self):
        self.assertTrue(os.environ.has_key("LAMBDAURL"))


if __name__ == '__main__':
    unittest.main()


class TestNormalize_stopcode(TestCase):
    def setUp(self):
        pass

    def test_single_digit(self):
        sc = normalize_stopcode("1")
        self.assertEqual(sc, "0001")

    def test_three_digit(self):
        sc = normalize_stopcode("101")
        self.assertEqual(sc, "0101")
