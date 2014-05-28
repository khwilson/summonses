"""
A parser for the NYPD's collission and summonses data.

:author: Kevin Wilson
:email: khwilson@gmail.com
:license: The Apache License, Version 2
"""
import arrow
from lxml import html
import urllib2
import urlparse

def _get_links(webpage, start_str, url=None):
    """
    Get a dictionary from an html document whose keys are Arrow dates and whose values are
    urls to the data.

    The idea is that the webpage has links that look like

    ::
        <a href="../some/path/to/here.html">start_str[and_more] August 2011</a>

    We parse these links and return the aforementioned dictionary. If url is not None, we
    will also do you the favor of parsing relative links by returning
    ``urlparse.urljoin(url, found_link_href)``.

    :param str webpage: The stringified version of an html page
    :param str start_str: The string to try to match in the link text
    :param str url: The prefix of all the urls to return
    :return: The described dict
    :rtype: dict[arrow.Arrow, str]
    """
    doc = html.document_fromstring(webpage)
    anchors = [link for link in doc.findall('.//a')
                            if link.text is not None and
                                link.text.startswith(start_str)]
    if url is None:
        join_func = lambda x: x
    else:
        join_func = lambda x: urlparse.urljoin(url, x)

    return {arrow.get(' '.join(link.text.strip().split(' ')[1:]), 'MMMM-YYYY'):
            join_func(link.attrib['href'])
            for link in anchors}

def get_summonses_from_webpage(webpage, url=None):
    """
    Get a dictionary from an html document whose keys are Arrow dates and whose values are
    urls to the data.

    The idea is that the webpage has links that look like

    ::
        <a href="../some/path/to/here.html">Summons[es] August 2011</a>

    We parse these links and return the aforementioned dictionary. If url is not None, we
    will also do you the favor of parsing relative links by returning
    ``urlparse.urljoin(url, found_link_href)``.

    :param str webpage: The stringified version of an html page
    :param str start_str: The string to try to match in the link text
    :param str url: The prefix of all the urls to return
    :return: The described dict
    :rtype: dict[arrow.Arrow, str]
    """
    return _get_links(webpage, 'Summons', url=url)

def get_collisions_from_webpage(webpage, url=None):
    """
    Get a dictionary from an html document whose keys are Arrow dates and whose values are
    urls to the data.

    The idea is that the webpage has links that look like

    ::
        <a href="../some/path/to/here.html">Collision[s] August 2011</a>

    We parse these links and return the aforementioned dictionary. If url is not None, we
    will also do you the favor of parsing relative links by returning
    ``urlparse.urljoin(url, found_link_href)``.

    :param str webpage: The stringified version of an html page
    :param str start_str: The string to try to match in the link text
    :param str url: The prefix of all the urls to return
    :return: The described dict
    :rtype: dict[arrow.Arrow, str]
    """
    return _get_links(webpage, 'Collision', url=url)

BASE_URL = 'http://www.nyc.gov/html/nypd/html/traffic_reports/traffic_report_archive_{year}.shtml'

def __get_page_with_retries(url, retries=5):
    """
    Try to retrieve a url up to retries times. If a 404 or 410 is received *or* we try
    retries times, return None. Else, return the string version of the url at the given
    page.

    :param str url: The url to try to retrieve
    :param int retries: The number of allowed retries
    :return: The stringified version of the page at url or None if it doesn't exist
    :rtype: str | None
    """
    num_retries = 0
    while num_retries < retries:
        try:
            opened_url = urllib2.urlopen(url)
            return opened_url.read()
        except urllib2.HTTPError as exc:
            if exc.code == 404 or exc.code == 410:
                return None
        num_retries += 1
    return None

def _iteratively_get_links(base_url, start_year, retries=5):
    """
    Assumes a url scheme that looks like

    ::
        http://here.com/is/a/lot/of/years/{year}/file.html

    where {year} is replaced by a range of years. This function will retrieve
    all such pages in a continuous range centered on start_year. Some caveats:
    #. ``base_url`` must contain exactly one formattable part, which must be ``{year}``.
    #. We quit trying to expand the range whenever we get a 404 or 410, but if we get any other
        error code, we'll retry up to ``retries`` times. If we run out of retries, we
        assume that no such page exists and stop our exploration in that direction of time.
    #. If base_url.format(year=start_year) does *not* exist, we will still try to explore in
        both directions. The justification for this is so that you can rerun this script
        by calling a ``current_year`` function and still get everything in the past even
        if the NYPD is being a bit slow on updating.

    :param str base_url: The base url. Must contain a single ``{year}`` formatting string.
    :param int start_year: The year to start looking from
    :param int retries: The number of retries allowed before assuming a page doesn't exist
    :return: The strings of the returned html
    :rtype: list[str]
    """
    retrieved_pages = []
    retrieved_page = __get_page_with_retries(base_url.format(year=start_year), retries=retries)
    if retrieved_page is not None:
        retrieved_pages.append(retrieved_page)

    # Forward in time
    year = start_year + 1
    while True:
        retrieved_page = __get_page_with_retries(base_url.format(year=year), retries=retries)
        if retrieved_page is not None:
            retrieved_pages.append(retrieved_page)
        else:
            break
        year += 1

    # Backward in time
    year = start_year - 1
    while True:
        retrieved_page = __get_page_with_retries(base_url.format(year=year), retries=retries)
        if retrieved_page is not None:
            retrieved_pages.append(retrieved_page)
        else:
            break
        year -= 1

    return retrieved_pages
