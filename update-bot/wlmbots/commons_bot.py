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
import re
import pywikibot
import mwparserfromhell

from wlmbots.lib.article_iterator import ArticleIterator, ArticleIteratorArgumentParser
from wlmbots.lib.template_replacer import TemplateReplacer
from wlmbots.lib.template_checker import TemplateChecker


class CommonsBot(object):

    def __init__(self, commons_site, wikipedia_site, article_iterator, template_checker):
        self.commons_site = commons_site
        self.wikipedia_site = wikipedia_site
        self.category_name = u"Images from Wiki Loves Monuments 2015 in Germany"
        self.start_time = default_start_time()
        article_iterator.article_callback = self.cb_check_article
        self.article_iterator = article_iterator
        self.template_checker = template_checker
        self.comment_pattern = re.compile(r"<-- LIST_CALLBACK_PARAMS (.+?)-->\n\n")

    def run_once(self, category=None):
        article_args = {
            "sortby": "timestamp",
            "starttime": self.start_time
        }
        if not category:
            category = pywikibot.Category(self.commons_site, self.category_name)
        self.article_iterator.iterate_articles(category, article_arguments=article_args)

    def cb_check_article(self, article, **kwargs):
        text = article.get()
        list_callback_params = self.comment_pattern.search(text)
        if not list_callback_params:
            return
        try:
            params = list_callback_params.group(1).strip()
            _, pagename, image_id = params.strip().split("|", 2)
        except ValueError:
            pywikibot.error(u"Invalid list callback param: '{}'".format(params))
            return
        try:
            self.insert_image(article.title(), pagename.strip(), image_id.strip())
        except CommonsBotException as err:
            pywikibot.error(err)
            return
        # TODO remove comment from commons_page

    def insert_image(self, commons_name, pagename, image_id):
        """ Insert image from page in Wikipedia """
        article = self.fetch_page(pagename)
        if not article.exists():
            raise CommonsBotException(u"Article is missing: '{}'".format(pagename))
        text = article.get()
        code = mwparserfromhell.parse(text)
        for template in code.filter_templates():
            if not self.template_checker.is_allowed_template:
                continue
            if self.template_checker.get_id(template) != image_id:
                continue
            if template.get("Bild").value.strip() != "":
                pywikibot.log("Image is already filled for id '{}' on page '{}', skipping ...".format(image_id, pagename))
                return False
            original_template = unicode(template)
            replacer = TemplateReplacer(template)
            replacer.set_value("Bild", commons_name)
            article.text = text.replace(original_template, unicode(replacer))
            article.save(summary=u"Bot: Bild aus Commons eingefügt")
            return True
        raise CommonsBotException(u"No template found with id '{}' on page '{}'".format(image_id, pagename))

    def fetch_page(self, pagename):
        """
        Helper function that returns a pywikibot article object.

        This function mainly to make mocking and testing easier.
        """
        return pywikibot.Page(self.wikipedia_site, pagename)


class CommonsBotException(Exception):
    pass


def default_start_time(date=None):
    if not date:
        date = datetime.date.today()
    return pywikibot.Timestamp(date.year, date.month, 1)


def main(*args):
    wikipedia_site = pywikibot.Site("de", "local")  # TODO use wikipeda instead
    commons_site = pywikibot.Site("commons", "commons")
    article_iterator = ArticleIterator(
        logging_callback=pywikibot.log,
    )
    parser = ArticleIteratorArgumentParser(article_iterator, None)
    checker = TemplateChecker()
    checker.load_config("config/templates.json")
    commons_bot = CommonsBot(commons_site, wikipedia_site, article_iterator, checker)
    for argument in pywikibot.handle_args(args):
        if argument.find("-category:") == 0:
            commons_bot.category_name = argument[10:]
            continue
        elif parser.check_argument(argument):
            continue
        elif argument.find("-start-at:") == 0:
            start_time = argument[10:] + "T0:00:00Z"
            commons_bot.start_time = pywikibot.Timestamp.fromISOformat(start_time)
    commons_bot.run_once()


if __name__ == "__main__":
    main()
