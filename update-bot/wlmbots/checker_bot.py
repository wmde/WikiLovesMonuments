#!/usr/bin/python
# -*- coding: utf-8 -*-
""" This bot checks the pages in the "Denkmalliste" categories for templates
    and unique IDs. It can create a result page from the check or just
    output the result.

Available command line options are:

-limit:N          Only check N number of pages

-category:NAME    Only check pages in category NAME

-outputpage:NAME  Write result to wiki page NAME instead of stdout

"""

from __future__ import unicode_literals

import codecs
import sys
import logging
import json
import itertools
import collections

import pywikibot
import mwparserfromhell

from lib.template_checker import TemplateChecker
from lib.pagelist import Pagelist

ERROR_MISSING_TEMPLATE = 1
ERROR_MISSING_IDS      = 2
ERROR_INVALID_IDS      = 4
ERROR_DUPLICATE_IDS    = 8

def check_for_errors(article, checker):
    if article.isRedirectPage():
        return
    text = article.get()
    if not checker.text_contains_templates(text):
        return {ERROR_MISSING_TEMPLATE: True}
    templates = mwparserfromhell.parse(text).filter_templates()
    errors = {
        ERROR_MISSING_IDS: 0,
        ERROR_INVALID_IDS: 0
    }
    ids = collections.Counter()
    for template in itertools.ifilter(checker.is_allowed_template, templates):
        row_id = checker.get_id(template)
        if not row_id:
            errors[ERROR_MISSING_IDS] += 1
            continue
        ids[row_id] += 1
        if not checker.has_valid_id(template):
            errors[ERROR_INVALID_IDS] += 1
    errors[ERROR_DUPLICATE_IDS] = {row_id: count for row_id, count in ids.iteritems() if count > 1}
    errors = {e: v for e, v in errors.iteritems() if v}
    return errors

def generate_result_page(results, pagelister):
    text = u""
    for category_results in results:
        heading = "=="
        category = category_results["category"]
        if not pagelister.root_category in category.categories():
            heading += "="
        text += u"{} {} {}\n".format(heading, category.title(), heading)
        num_errors = len(category_results["results"])
        text += u"{} Seiten geprüft, {} ohne Probleme\n".format(category_results["pages_checked"], category_results["pages_checked"] - num_errors)
        text += u"{{Fehler in Denkmallisten Tabellenkopf}}\n"
        for result in category_results["results"]:
            errors = {
                ERROR_MISSING_TEMPLATE: "",
                ERROR_MISSING_IDS: "",
                ERROR_INVALID_IDS: "",
                ERROR_DUPLICATE_IDS: ""
            }
            severity = min(result["errors"].keys())
            errors.update(result["errors"])
            duplicate_ids = ", ".join(errors[ERROR_DUPLICATE_IDS])
            text += u"{{{{Fehler in Denkmallisten Tabellenzeile|Titel={}|Kein_Template={}|IDs_fehlen={}|IDs_ungueltig={}|IDs_doppelt={}|Level={}}}}}\n".format(
                result["title"], errors[ERROR_MISSING_TEMPLATE], errors[ERROR_MISSING_IDS], errors[ERROR_INVALID_IDS], duplicate_ids, severity
            )
        text += "|}\n\n"
    return text

def get_results_for_county(checker, articles, limit, counter=0):
    results = []
    for article in articles:
        counter += 1
        if not counter % 100:
            pywikibot.log("Fetching Page {} ({})".format(counter, article.title()))
        if limit and counter > limit:
            break
        errors = check_for_errors(article, checker)
        if errors:
            results.append({
                "title": article.title(),
                "errors": errors
            })
    return counter, results

def generate_config_table(checker_config):
    line_fmt = "|-\n|[[Vorlage:{}|{}]]\n|{}\n|{}\n"
    text = '{| class="wikitable"\n|-\n!Vorlage!!Bezeichner ID!!Format ID\n'
    for template_name, config in sorted(checker_config.items()):
        text += line_fmt.format(template_name, template_name, config["id"], config["id_check_description"])
    text += "|}\n\n"
    return text

def main(*args):
    UTF8Writer = codecs.getwriter('utf8')
    output_destination = UTF8Writer(sys.stdout)
    verbosity = logging.ERROR
    limit = 0
    catname = "ALL"
    for argument in pywikibot.handle_args(args):
        if argument.find("-limit:") == 0:
            limit = int(argument[7:])
        elif argument.find("-category:") == 0:
            catname = argument[10:]
        elif argument.find("-outputpage:") == 0:
            outputpage = argument[12:]
    logging.basicConfig(level=verbosity, stream=output_destination)
    site = pywikibot.Site()
    counter = 0
    results = []
    with open("template_config.json", "r") as tplconf:
        checker_config = json.load(tplconf)
    pagelister = Pagelist(site)
    checker = TemplateChecker(checker_config)
    if catname == "ALL":
        categories = pagelister.get_county_categories()
    else:
        categories = [pywikibot.Category(site, catname)]
    for category in categories:
        prev_count = counter
        counter, result = get_results_for_county(checker, category.articles(), limit, counter)
        if result:
            results.append({
                "category": category,
                "results": result,
                "pages_checked": counter - (prev_count + 1) # Counter is already increased by 1
            })
        if limit and counter > limit:
            break
    result_page = generate_result_page(results, pagelister)
    result_page += "== Zulässige Vorlagen ==\nDie Seiten wurden mit folgenden zulässigen Vorlagen und Einstellungen geprüft:\n"
    result_page += generate_config_table(checker_config)
    if outputpage:
        article = pywikibot.Page(site, outputpage)
        article.text = result_page
        article.save()
        # TODO check if the templates exist and if they don't, create the template pages from wiki_templates
    else:
        pywikibot.output(result_page)

if __name__ == "__main__":
    main()
