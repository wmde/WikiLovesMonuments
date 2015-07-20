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

from template_replacer import TemplateReplacer
# TODO: import TableReplacer

WLM_PLACEHOLDER = '<-- link to commons placeholder #commonscat# -->' # TODO proper placeholder

def add_placeholders(article):
    logging.info("{}".format(article.title()))
    if article.isRedirectPage():
        return
    text = article.get()
    # TODO check text from page for general commons category, if none is found, return with error msg
    commonscat = "Foo"
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
            # TODO check template for commonscat and assign it to row_commonscat
            row_commonscat = commonscat
            placeholder = WLM_PLACEHOLDER.replace("#commonscat#", row_commonscat)
            logging.debug("   ... inserting placeholder in {}".format(template))
            replacer.set_value('Bild', placeholder)
            text = text.replace(unicode(template), unicode(replacer))
    return text

def replace_in_tables(text, commonscat):
    # TODO: Use table parser to replace table rows
    return text

def main(*args):
    UTF8Writer = codecs.getwriter('utf8')
    output_destination = UTF8Writer(sys.stdout)
    verbosity = logging.ERROR
    for argument in pywikibot.handle_args(args):
        if argument == "-v":
            verbosity = logging.WARNING
        elif argument == "-vv":
            verbosity = logging.INFO
        elif argument == "-vvv":
            verbosity = logging.DEBUG
    logging.basicConfig(level=verbosity, stream=output_destination)
    site = pywikibot.Site()
    limit = 100
    counter = 0
    # TODO use pagelist class and iterate over categories
    for article in pywikibot.Category(site, u"Liste_(Kulturdenkmale_in_Baden-Württemberg)").articles():
        add_placeholders(article)
        counter += 1
        if counter > limit:
            break

if __name__ == "__main__":
    main()
