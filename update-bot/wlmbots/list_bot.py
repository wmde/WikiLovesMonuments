#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script generates a list of page names that can be used for exporting the
relevant articles or getting an overview.

Available command line options are:

-out:file         Write output of all categories into a single file called
                  "Denkmallistenliste.txt".

-out:categories   Write output of each category into a single file, named after
                  the category.

-fmt:wiki         Output page name as Wiki links

-fmt:url          Output page names as URLs to the articles

-list-cat-only    Output only the names of the main categories, not the page names.
                  Cannot be used together with -out:categories
"""

from __future__ import unicode_literals

import codecs
import sys

import pywikibot
from wlmbots.lib.pagelist import Pagelist


def export_to_file(outfile, items, formatstring=u"{}\n"):
    """ Write article to file

        items: array or generator with objects that support the title method.
    """
    for article in items:
        outfile.write(formatstring.format(article.title()))


def main(*args):
    utf8_writer = codecs.getwriter('utf8')
    single_categories = False
    output_destination = utf8_writer(sys.stdout)
    formatstring = "{}\n"
    categories_only = False
    for arg in pywikibot.handle_args(*args):
        if arg == "-out:categories":
            single_categories = True
        elif arg == "-out:file":
            output_destination = codecs.open("Denkmallistenliste.txt", "w", 'utf-8')
        elif arg == "-fmt:wiki":
            formatstring = "[[{}]]\n"
        elif arg == "-fmt:url":
            formatstring = "https://de.wikipedia.org/wiki/{}\n"
        elif arg == "-list-cat-only":
            categories_only = True

    site = pywikibot.Site()
    page_list = Pagelist(site)

    if categories_only and not single_categories:
        export_to_file(output_destination, page_list.get_county_categories(False), formatstring)
        return

    if single_categories:
        for category in page_list.get_county_categories():
            with codecs.open(category.title() + u".txt", "w", 'utf-8') as outfile:
                export_to_file(outfile, category.articles(), formatstring)
    else:
        export_to_file(output_destination, page_list.get_list_articles(), formatstring)


if __name__ == "__main__":
    main()
