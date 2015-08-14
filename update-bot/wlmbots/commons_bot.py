#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This bot checks a Commons category for new entries, checks the entry pages
for special comments and inserts links to these pages in the German Wikipedia.

Available command line options are:

-category:NAME    Category to use instead of "Images from Wiki Loves Monuments 2015 in Germany"

-start-at:        Date from which to start requesting pages. Defaults to start of month. Format YYYY-MM-DD

-sleep-seconds:N  Sleep N seconds betwen runs

-limit:N          Stop after N processed Commons pages

-once:            Run only once (by default it runs continously)

-local-media:     Use the local wiki instead of Wikimedia Commons

"""

from __future__ import unicode_literals
import time
import datetime
import re
import pywikibot
import mwparserfromhell

from wlmbots.lib.article_iterator import ArticleIterator, ArticleIteratorArgumentParser
from wlmbots.lib.template_replacer import TemplateReplacer
from wlmbots.lib.template_checker import TemplateChecker


class CommonsBot(object):

    comment_pattern = re.compile(r"<!-- LIST_CALLBACK_PARAMS (.+?)-->\n\n")
    prefix_pattern = re.compile(r"^(?:File|Datei):")

    def __init__(self, wikipedia_site, article_iterator, template_checker):
        self.wikipedia_site = wikipedia_site
        article_iterator.article_callback = self.cb_check_article
        self.article_iterator = article_iterator
        self.template_checker = template_checker
        self.sleep_seconds = 30
        self.logger = pywikibot

    def run_once(self, start_time, category):
        article_args = {
            "sortby": "timestamp",
            "starttime": start_time
        }
        self.article_iterator.iterate_articles(category, article_arguments=article_args)

    def run_continous(self, start_time, category):
        article_args = {
            "sortby": "timestamp",
            "starttime": start_time
        }
        counter = 0
        while True:
            now = pywikibot.Timestamp.now()
            counter += self.article_iterator.iterate_articles(category, counter, article_args)
            article_args["starttime"] = now
            if self.article_iterator.limit_reached(counter, 0):
                break
            time.sleep(self.sleep_seconds)

    def cb_check_article(self, article, **kwargs):
        text = article.get()
        list_callback_params = self.comment_pattern.search(text)
        if not list_callback_params:
            return
        try:
            params = list_callback_params.group(1).strip()
            _, pagename, image_id = params.strip().split("|", 2)
        except ValueError:
            self.logger.error(u"Invalid list callback param: '{}'".format(params))
            return
        try:
            self.insert_image(article.title(), pagename.strip(), image_id.strip())
        except CommonsBotException as err:
            self.logger.error(err)
            return
        # remove comment from commons_page
        article.text = text.replace(list_callback_params.group(0), '')
        article.save("Bot: Removed comment after inserting image in Wikipedia article")

    def insert_image(self, commons_name, pagename, image_id):
        """ Insert image from page in Wikipedia """
        article = self.fetch_page(pagename)
        if not article.exists():
            raise CommonsBotException(u"Article is missing: '{}'".format(pagename))
        text = article.get()
        code = mwparserfromhell.parse(text)
        for template in self.template_checker.filter_allowed_templates(code.filter_templates()):
            if self.template_checker.get_id(template) != image_id:
                continue
            if template.get("Bild").value.strip() != "":
                self.logger.log("Image is already filled for id '{}' on page '{}', skipping ...".format(image_id, pagename))
                return False
            original_template = unicode(template)
            replacer = TemplateReplacer(template)
            replacer.set_value("Bild", self.prefix_pattern.sub('', commons_name))
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


def first_day_of_month(date=None):
    if not date:
        date = datetime.date.today()
    return pywikibot.Timestamp(date.year, date.month, 1)


def main(*args):
    wikipedia_site = pywikibot.Site()  # Use the site configured in params/user-config
    commons_site = pywikibot.Site("commons", "commons")
    article_iterator = ArticleIterator(
        logging_callback=pywikibot.log,
    )
    parser = ArticleIteratorArgumentParser(article_iterator, None)
    checker = TemplateChecker()
    checker.load_config("config/templates.json")
    commons_bot = CommonsBot(wikipedia_site, article_iterator, checker)
    run_cmd = commons_bot.run_continous
    category_name = u"Images from Wiki Loves Monuments 2015 in Germany"
    start_time = first_day_of_month()
    for argument in pywikibot.handle_args(args):
        if argument.find("-category:") == 0:
            category_name = argument[10:]
            continue
        elif parser.check_argument(argument):
            continue
        elif argument.find("-start-at:") == 0:
            start_time_iso = argument[10:] + "T0:00:00Z"
            start_time = pywikibot.Timestamp.fromISOformat(start_time_iso)
        elif argument.find("-sleep-seconds:") == 0 and int(argument[15:]) > 0:
            commons_bot.sleep_seconds = int(argument[15:])
        elif argument == "-once":
            run_cmd = commons_bot.run_once
        elif argument == "-local-media":
            commons_site = wikipedia_site
    category = pywikibot.Category(commons_site, category_name)
    run_cmd(start_time, category)


if __name__ == "__main__":
    main()
