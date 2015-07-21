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

from template_replacer import TemplateReplacer
# TODO: import TableReplacer

WLM_PLACEHOLDER = '<-- link to commons placeholder #commonscat# -->' # TODO proper placeholder

def add_placeholders(article):
    logging.info("{}".format(article.title()))
    if article.isRedirectPage():
        return
    text = article.get()
    commonscat = get_commonscat_from_weblinks(text)
    if not commonscat:
        logging.error("  {} has no commonscat template in weblinks section".format(article.title()))
        return
    text_with_placeholders_in_templates = replace_in_templates(text, commonscat)
    text_with_placeholders_in_tables = replace_in_tables(text_with_placeholders_in_templates, commonscat)
    if text != text_with_placeholders_in_tables:
        # TODO store new text
        logging.info("  Updated article with placeholders")
        logging.debug(text_with_placeholders_in_tables)

def get_commonscat_from_weblinks(text):
    header_pos = re.search(r'=+\s+Weblinks', text, re.IGNORECASE)
    if not header_pos:
        return ""
    weblink_text = text[header_pos.start(0):]
    for template in mwparserfromhell.parse(weblink_text).filter_templates():
        if template.name.matches("Commonscat"):
            return unicode(template.params[0])
    return ""


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
    # TODO: Use table parser to replace table rows
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
