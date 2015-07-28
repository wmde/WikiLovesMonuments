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

import pywikibot
import mwparserfromhell

from wlmbots.lib.template_checker import TemplateChecker
from wlmbots.lib.pagelist import Pagelist


def generate_result_page(results, pagelister):
    text = u""
    for category_results in results:
        heading = "=="
        category = category_results["category"]
        if pagelister.root_category not in category.categories():
            heading += "="
        text += u"{} {} {}\n".format(heading, category.title(), heading)
        num_errors = len(category_results["results"])
        text += u"{} Seiten geprüft, {} ohne Probleme\n".format(category_results["pages_checked"],
                                                                category_results["pages_checked"] - num_errors)
        text += u"{{Fehler in Denkmallisten Tabellenkopf}}\n"
        for result in category_results["results"]:
            errors = {
                TemplateChecker.ERROR_MISSING_TEMPLATE: "",
                TemplateChecker.ERROR_MISSING_IDS: "",
                TemplateChecker.ERROR_INVALID_IDS: "",
                TemplateChecker.ERROR_DUPLICATE_IDS: ""
            }
            severity = min(result["errors"].keys())
            errors.update(result["errors"])
            duplicate_ids = ", ".join(errors[TemplateChecker.ERROR_DUPLICATE_IDS])
            text += u"{{{{Fehler in Denkmallisten Tabellenzeile|Titel={}|Kein_Template={}|IDs_fehlen={}|IDs_ungueltig={}|IDs_doppelt={}|Level={}}}}}\n".format(
                result["title"], errors[TemplateChecker.ERROR_MISSING_TEMPLATE], errors[TemplateChecker.ERROR_MISSING_IDS],
                errors[TemplateChecker.ERROR_INVALID_IDS], duplicate_ids, severity
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
        errors = checker.check_article_for_errors(article)
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
    utf8_writer = codecs.getwriter('utf8')
    output_destination = utf8_writer(sys.stdout)
    verbosity = logging.ERROR
    limit = 0
    catname = "ALL"
    outputpage = None
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
    pagelister = Pagelist(site)
    checker = TemplateChecker()
    checker.load_config("template_config.json")
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
                "pages_checked": counter - (prev_count + 1)  # Counter is already increased by 1
            })
        if limit and counter > limit:
            break
    result_page = generate_result_page(results, pagelister)
    result_page += "== Zulässige Vorlagen ==\nDie Seiten wurden mit folgenden zulässigen Vorlagen und Einstellungen geprüft:\n"
    result_page += generate_config_table(checker.config)
    if outputpage:
        article = pywikibot.Page(site, outputpage)
        old_text = article.get()
        if old_text != result_page:
            article.text = result_page
            article.save(summary="Bot: Update der Ergebnisliste")
        else:
            pywikibot.log("Result page has not changed, skipping update ...")
        # TODO check if the templates exist and if they don't, create the template pages from wiki_templates
    else:
        pywikibot.output(result_page)


if __name__ == "__main__":
    main()
