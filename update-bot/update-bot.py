# -*- coding: utf-8 -*-
# This bot checks which templates are used on the wlm pages

from __future__ import unicode_literals

import pywikibot
from os.path import join
from pywikibot import config
import codecs
import sys
import mwparserfromhell
import random
import operator

from template_replacer import TemplateReplacer
# TODO: import TableReplacer

WLM_PLACEHOLDER = '<-- link to commons placeholder #commonscat# -->' # TODO proper placeholder

def add_placeholders(article, output_destination, verbose_output=False):
    if verbose_output:
        output_destination.write("{}\n".format(article.title()))
    if article.isRedirectPage():
        return
    text = article.get()
    # TODO check text from page for general commons category, if none is found, return with error msg
    commonscat = "Foo"
    text_with_placeholders_in_templates = replace_in_templates(text, commonscat, output_destination, verbose_output)
    text_with_placeholders_in_tables = replace_in_tables(text_with_placeholders_in_templates, commonscat, output_destination, verbose_output)
    if text != text_with_placeholders_in_tables:
        # TODO store new text
        if verbose_output:
            output_destination.write("Updated article with placeholders\n")

def replace_in_templates(text, commonscat, output_destination, verbose_output=False):
    global WLM_PLACEHOLDER
    # fail fast
    if text.find("Tabellenzeile") == -1:
        return text
    code = mwparserfromhell.parse(text)
    for template in code.filter_templates():
        if template.name.find("Tabellenzeile") == -1:
            return
        replacer = TemplateReplacer(t)
        if replacer.param_is_empty("Bild"):
            # TODO check template for commonscat and assign it to row_commonscat
            row_commonscat = commonscat
            placeholder = WLM_PLACEHOLDER.replace("#commonscat#", row_commonscat)
            if verbose_output:
                output_destination.write("   ... inserting placeholder in {} \n".format(template))
            replacer.set_value('Bild', placeholder)
            text = text.replace(unicode(template), unicode(replacer))
    return text

def replace_in_tables(text, commonscat, output_destination, verbose_output=False):
    # TODO: Use table parser to replace table rows
    return text

def main(*args):
    UTF8Writer = codecs.getwriter('utf8')
    output_destination = UTF8Writer(sys.stdout)
    verbose = False

    site = pywikibot.Site()
    limit = 100
    counter = 0
    # TODO use pagelist class and iterate over categories
    for article in pywikibot.Category(site, u"Liste_(Kulturdenkmale_in_Baden-Württemberg)").articles():
        add_placeholders(article, output_destination, True)
        counter += 1
        if counter > limit:
            break

if __name__ == "__main__":
    main()
