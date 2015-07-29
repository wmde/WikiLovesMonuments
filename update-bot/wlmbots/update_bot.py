#!/usr/bin/python
# -*- coding: utf-8 -*-
# This bot inserts placeholders to Wikimedia Commons on all the monument pages

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

WLM_PLACEHOLDER = '<-- link to commons placeholder "#commonscat#" -->'  # TODO proper placeholder

class UpdateBot(object):

    def __init__(self, commonscat_mapper):
        self.commonscat_mapper = commonscat_mapper

    def cb_add_placeholders(self, article):
        logging.info("%s", article.title())
        if article.isRedirectPage():
            return
        text = article.get()
        commonscat = self.commonscat_mapper.get_commonscat_from_category_links(text)
        if not commonscat:
            logging.error("  %s has no mapped category link.", article.title())
            return
        text_with_placeholders_in_templates = self.replace_in_templates(text)
        if text != text_with_placeholders_in_templates:
            # TODO store new text
            logging.info("  Updated article with placeholders")
            logging.debug(text_with_placeholders_in_templates)

    def replace_in_templates(self, text):
        global WLM_PLACEHOLDER
        # fail fast
        if text.find("Tabellenzeile") == -1:
            logging.info("   no templates found.")
            return text
        code = mwparserfromhell.parse(text)
        for template in code.filter_templates():
            if template.name.find("Tabellenzeile") == -1:
                continue
            replacer = TemplateReplacer(template)
            if replacer.param_is_empty("Bild"):
                row_commonscat = self.commonscat_mapper.get_commonscat(text, template)
                placeholder = WLM_PLACEHOLDER.replace("#commonscat#", row_commonscat)
                replacer.set_value('Bild', placeholder)
                text = text.replace(unicode(template), unicode(replacer))
        return text


def main(*args):
    utf8_writer = codecs.getwriter('utf8')
    output_destination = utf8_writer(sys.stdout)
    verbosity = logging.ERROR
    site = pywikibot.Site()
    pagelister = Pagelist(site)
    mapper = CommonscatMapper()
    mapper.load_mapping("config/commonscat_mapping.json")
    update_bot = UpdateBot()
    article_iterator = ArticleIterator(
        article_callback=update_bot.cb_add_placeholders,
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
