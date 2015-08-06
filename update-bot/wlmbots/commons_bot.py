#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This bot checks a commons category for new entries, checks the entry pages
for special comments and inserts links to these pages in the German Wikipedia.

Available command line options are:

-category:NAME    Category to use instead of "Images from Wiki Loves Monuments 2015 in Germany"

-start-at:        Date from which to start requesting pages. Defaults to start of month. Format YYYY-MM-DD

"""

from __future__ import unicode_literals
import datetime
import pywikibot


class CommonsBot(object):

    def __init__(self, commons_site, wikipedia_site):
        self.commons_site = commons_site
        self.wikipedia_site = wikipedia_site
        self.category_name = u"Images from Wiki Loves Monuments 2015 in Germany"
        self.start_time = default_start_time()

    def run_once(self):
        for image in self.get_new_pages():
            # just for testing
            print image.title()
            print image.get()
            return
        # TODO insert image from page in wikipedia
        # TODO remove comment from commons_page

    def get_new_pages(self, category=None):
        if not category:
            category = pywikibot.Category(self.commons_site, self.category_name)
        return category.articles(sortby="timestamp", starttime=self.start_time)


def default_start_time(date=None):
    if not date:
        date = datetime.date.today()
    return pywikibot.Timestamp(date.year, date.month, 1)


def main(*args):
    wikipedia_site = pywikibot.Site("de", "local") # TODO use wikipeda instead
    commons_site = pywikibot.Site("commons", "commons")
    commons_bot = CommonsBot(commons_site, wikipedia_site)
    for argument in pywikibot.handle_args(args):
        if argument.find("-category:") == 0:
            commons_bot.category_name = argument[10:]
        elif argument.find("-start-at:") == 0:
            start_time = argument[10:] + "T0:00:00Z"
            commons_bot.start_time = pywikibot.Timestamp.fromISOformat(start_time)
    commons_bot.run_once()


if __name__ == "__main__":
    main()
