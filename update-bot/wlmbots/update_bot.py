#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This bot inserts Commons Category names in all supported "Tabellenzeile" templates
"""

from __future__ import unicode_literals

import codecs
import sys
import logging

import pywikibot
import mwparserfromhell

from wlmbots.lib.commonscat_mapper import CommonscatMapper
from wlmbots.lib.template_replacer import TemplateReplacer
from wlmbots.lib.pagelist import Pagelist
from wlmbots.lib.article_iterator import ArticleIterator, ArticleIteratorArgumentParser
from wlmbots.lib.template_checker import TemplateChecker

class UpdateBot(object):

    def __init__(self, commonscat_mapper, template_checker):
        self.commonscat_mapper = commonscat_mapper
        self.template_checker = template_checker
        self.summary = u"Bot: Commons Kategorie in Tabellenzeile Vorlagen einfügen"

    def cb_modify_templates(self, article, **kwargs):
        logging.info("%s", article.title())
        if article.isRedirectPage():
            return
        errors = self.template_checker.check_article_for_errors(article)
        if TemplateChecker.ERROR_MISSING_TEMPLATE in errors:
            logging.info("  No templates found, skipping")
            return
        text = article.get()
        commonscat = self.commonscat_mapper.get_commonscat_from_category_links(text)
        if not commonscat:
            logging.error("  %s has no mapped category link.", article.title())
            return
        text_with_commons_cat = self.replace_in_templates(text)
        if text != text_with_commons_cat:
            article.text = text_with_commons_cat
            article.save(summary=self.summary)
            logging.info("  Updated article with commons category")
            logging.debug(text_with_commons_cat)

    def replace_in_templates(self, text):
        code = mwparserfromhell.parse(text)
        for template in self.template_checker.filter_allowed_templates(code.filter_templates()):
            replacer = TemplateReplacer(template)
            if replacer.param_is_empty("Commonscat"):
                row_commonscat = self.commonscat_mapper.get_commonscat(text, template)
                replacer.set_value('Commonscat', row_commonscat.replace("Category:", ""))
                text = text.replace(unicode(template), unicode(replacer))
        return text


def main(*args):
    utf8_writer = codecs.getwriter('utf8')
    output_destination = utf8_writer(sys.stdout)
    verbosity = logging.ERROR
    site = pywikibot.Site()
    pagelister = Pagelist(site)
    commonscat_mapper = CommonscatMapper()
    commonscat_mapper.load_mapping("config/commonscat_mapping.json")
    commonscat_mapper.load_subcategories_into_map(site)
    checker = TemplateChecker()
    checker.load_config("config/templates.json")
    update_bot = UpdateBot(commonscat_mapper, checker)
    article_iterator = ArticleIterator(
        article_callback=update_bot.cb_modify_templates,
        categories=pagelister.get_county_categories()
    )
    parser = ArticleIteratorArgumentParser(article_iterator, pagelister)
    for argument in pywikibot.handle_args(args):
        if parser.check_argument(argument):
            continue
        elif argument == "-v":
            verbosity = logging.WARNING
        elif argument == "-vv":
            verbosity = logging.INFO
        elif argument == "-vvv":
            verbosity = logging.DEBUG
    logging.basicConfig(level=verbosity, stream=output_destination)
    article_iterator.iterate_categories()


if __name__ == "__main__":
    main()
