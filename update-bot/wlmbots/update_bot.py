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


WLM_PLACEHOLDER = '<-- link to commons placeholder "#commonscat#" -->'  # TODO proper placeholder


def add_placeholders(article):
    logging.info("{}".format(article.title()))
    if article.isRedirectPage():
        return
    text = article.get()
    commonscat = CommonscatMapper().get_commonscat_from_category_links(text)
    if not commonscat:
        logging.error("  {} has no mapped category link.".format(article.title()))
        return
    text_with_placeholders_in_templates = replace_in_templates(text)
    if text != text_with_placeholders_in_templates:
        # TODO store new text
        logging.info("  Updated article with placeholders")
        logging.debug(text_with_placeholders_in_templates)


def replace_in_templates(text):
    global WLM_PLACEHOLDER
    # fail fast
    if text.find("Tabellenzeile") == -1:
        logging.info("   no templates found.")
        return text
    mapper = CommonscatMapper()
    code = mwparserfromhell.parse(text)
    for template in code.filter_templates():
        if template.name.find("Tabellenzeile") == -1:
            continue
        replacer = TemplateReplacer(template)
        if replacer.param_is_empty("Bild"):
            row_commonscat = mapper.get_commonscat(text, template)
            placeholder = WLM_PLACEHOLDER.replace("#commonscat#", row_commonscat)
            replacer.set_value('Bild', placeholder)
            text = text.replace(unicode(template), unicode(replacer))
    return text


def main(*args):
    utf8_writer = codecs.getwriter('utf8')
    output_destination = utf8_writer(sys.stdout)
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
