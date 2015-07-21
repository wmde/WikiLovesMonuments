# -*- coding: utf-8 -*-
# This bot inserts placeholders to Wikimedia Commons on all the monument pages

from __future__ import unicode_literals

import pywikibot
from os.path import join
from pywikibot import config
import codecs
import sys
import mwparserfromhell
import random
import operator
import logging
import re

from commonscat_mapper import CommonscatMapper
from template_replacer import TemplateReplacer
# TODO: import TableReplacer

WLM_PLACEHOLDER = '<-- link to commons placeholder "#commonscat#" -->' # TODO proper placeholder

def add_placeholders(article):
    logging.info("{}".format(article.title()))
    if article.isRedirectPage():
        return
    text = article.get()
    commonscat = CommonscatMapper().get_commonscat_from_links(text)
    if not commonscat:
        logging.error("  {} has no mapped category link.".format(article.title()))
        return
    text_with_placeholders_in_templates = replace_in_templates(text, commonscat)
    text_with_placeholders_in_tables = replace_in_tables(text_with_placeholders_in_templates, commonscat)
    if text != text_with_placeholders_in_tables:
        # TODO store new text
        logging.info("  Updated article with placeholders")
        logging.debug(text_with_placeholders_in_tables)

def replace_in_templates(text, commonscat):
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
            # TODO ask Kai if row commonscat can/should override page commoncat
            row_commonscat = commonscat
            placeholder = WLM_PLACEHOLDER.replace("#commonscat#", row_commonscat)
            replacer.set_value('Bild', placeholder)
            text = text.replace(unicode(template), unicode(replacer))
    return text

def replace_in_tables(text, commonscat):
    # TODO Find table starts on page {|-
    # TODO parse table headings of each table to get a dictionary of heading => column_index
    # TODO find beginning of each table row, and use table_replacer to check/change image column of each row
    return text

def main(*args):
    UTF8Writer = codecs.getwriter('utf8')
    output_destination = UTF8Writer(sys.stdout)
    verbosity = logging.ERROR
    limit = 0
    for argument in pywikibot.handle_args(args):
        if argument == "-v":
            verbosity = logging.WARNING
        elif argument == "-vv":
            verbosity = logging.INFO
        elif argument == "-vvv":
            verbosity = logging.DEBUG
        elif argument.find("-limit=") == 0:
            limit = int(argument[7:])
    logging.basicConfig(level=verbosity, stream=output_destination)
    site = pywikibot.Site()
    counter = 0
    # TODO use pagelist class and iterate over categories
    for article in pywikibot.Category(site, u"Liste_(Kulturdenkmale_in_Baden-Württemberg)").articles():
        add_placeholders(article)
        counter += 1
        if limit and counter > limit:
            break

if __name__ == "__main__":
    main()
