"""
:author: Kevin Wilson
:email: khwilson@gmail.com
:license: The Apache License, Version 2
"""
import arrow
import pkg_resources
from summonses import parser as undertest

import unittest

class TestWebpageParsing(unittest.TestCase):
    """
    This class is concerned with testing our parsing of webpages.
    """

    webpage = """
        <!doctype html>
        <html>
            <head><title>A Fake Webpage</title></head>
            <body>
            Here is a lot of text <div> floating tag oh no!!!
            and then <a href="../../random_url1.shtml">Summonses August 2012</a>
            and then <a href="random_url2.shtml">Collisions August 2015 </a>
            and then <a href="random_url3.shtml">Summonses December 2011</a>
            and then <a href="../../random_url4.shtml">Collisions June 2013</a>
            with a <a href="http://hello.com/thing.html">Random January 2000</a>
                thrown in
            </body>
        </html>"""

    def test_get_summonses_from_webpage_without_url(self):
        actual_summons = undertest.get_summonses_from_webpage(TestWebpageParsing.webpage)
        expected_summons = {
            arrow.get("August 2012", 'MMMM-YYYY'): "../../random_url1.shtml",
            arrow.get("December 2011", 'MMMM-YYYY'): "random_url3.shtml"
        }
        self.assertEqual(expected_summons, actual_summons)

    def test_get_summonses_from_webpage_with_url(self):
        actual_summons = undertest.get_summonses_from_webpage(TestWebpageParsing.webpage,
            url="http://my.com/absolute/long/path.html")
        expected_summons = {
            arrow.get("August 2012", 'MMMM-YYYY'): "http://my.com/random_url1.shtml",
            arrow.get("December 2011", 'MMMM-YYYY'): "http://my.com/absolute/long/random_url3.shtml"
        }
        self.assertEqual(expected_summons, actual_summons)

    def test_get_collisions_from_webpage_without_url(self):
        actual_collision = undertest.get_collisions_from_webpage(TestWebpageParsing.webpage)
        expected_collision = {
            arrow.get("June 2013", 'MMMM-YYYY'): "../../random_url4.shtml",
            arrow.get("August 2015", 'MMMM-YYYY'): "random_url2.shtml"
        }
        self.assertEqual(expected_collision, actual_collision)

    def test_get_collisions_from_webpage_with_url(self):
        actual_collision = undertest.get_collisions_from_webpage(TestWebpageParsing.webpage,
            url="http://my.com/absolute/long/path.html")
        expected_collision = {
            arrow.get("June 2013", 'MMMM-YYYY'): "http://my.com/random_url4.shtml",
            arrow.get("August 2015", 'MMMM-YYYY'): "http://my.com/absolute/long/random_url2.shtml"
        }
        self.assertEqual(expected_collision, actual_collision)

    def test__get_links_without_url(self):
        actual_dict = undertest._get_links(TestWebpageParsing.webpage, 'Random')
        expected_dict = {
            arrow.get("January 2000", 'MMMM-YYYY'): "http://hello.com/thing.html"
        }
        self.assertEqual(expected_dict, actual_dict)

    def test__get_links_with_url(self):
        actual_dict = undertest._get_links(TestWebpageParsing.webpage, 'Random',
            url="http://my.com/absolute/long/path.html")
        expected_dict = {
            arrow.get("January 2000", 'MMMM-YYYY'): "http://hello.com/thing.html"
        }
        self.assertEqual(expected_dict, actual_dict)

    def test_with_fixture(self):
        actual_summonses = \
            undertest.get_summonses_from_webpage(
                pkg_resources.resource_string(__name__, 'fixture.html'))
        self.assertEqual(5, len(actual_summonses))
        self.assertEqual({arrow.get("%s 2011" % month, 'MMMM-YYYY') for month in ("August", "September", "October", "November", "December")},
                        set(actual_summonses.keys()))


if __name__ == '__main__':
    unittest.main()
