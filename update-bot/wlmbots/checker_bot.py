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

import pywikibot

from wlmbots.lib.template_checker import TemplateChecker
from wlmbots.lib.pagelist import Pagelist
from wlmbots.lib.article_iterator import ArticleIterator, ArticleIteratorArgumentParser


class CheckerBot(object):

    def __init__(self, template_checker):
        self.results = []
        self.article_results = []
        self.previous_count = 0
        self.checker = template_checker


    def generate_result_page(self, pagelister):
        text = u""
        for category_results in self.results:
            text += self.generate_category_result_header(category_results, pagelister)
            text += self.generate_category_result_table(category_results)
        return text


    def generate_category_result_header(self, results, pagelister):
        text = u""
        heading = "=="
        category = results["category"]
        if pagelister.root_category not in category.categories():
            heading += "="
        text += u"\n{} {} {}\n".format(heading, category.title(), heading)
        num_errors = len(results["results"])
        pages_ok = results["pages_checked"] - num_errors
        text += u"{} Seiten geprüft".format(results["pages_checked"])
        if num_errors == 0:
            text += u", alle Seiten werden unterstützt."
        elif num_errors == results["pages_checked"]:
            text += u", keine der Seiten wird unterstützt"
        else:
            text += u", {} Seiten werden unterstützt ({:.0%}), {} Seiten nicht unterstützt ({:.0%}).".format(
                pages_ok, pages_ok / results["pages_checked"], num_errors, num_errors / results["pages_checked"]
            )
        text += "\n"
        return text


    def generate_category_result_table(self, results):
        text = u"{{Fehler in Denkmallisten Tabellenkopf}}\n"
        for result in results["results"]:
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


    def generate_config_table(self):
        line_fmt = "|-\n|[[Vorlage:{}|{}]]\n|{}\n|{}\n"
        text = '{| class="wikitable"\n|-\n!Vorlage!!Bezeichner ID!!Format ID\n'
        for template_name, config in sorted(self.checker.config.items()):
            text += line_fmt.format(template_name, template_name, config["id"], config["id_check_description"])
        text += "|}\n\n"
        return text


    def cb_store_category_result(self, category, counter=0, **kwargs):
        if self.article_results:
            self.results.append({
                "category": category,
                "results": self.article_results,
                "pages_checked": counter - self.previous_count
            })
        self.article_results = []
        self.previous_count = counter


    def cb_check_article(self, article, **kwargs):
        errors = self.checker.check_article_for_errors(article)
        if errors:
            self.article_results.append({
                "title": article.title(),
                "errors": errors
            })


def main(*args):
    outputpage = None
    site = pywikibot.Site()
    pagelister = Pagelist(site)
    checker = TemplateChecker()
    checker.load_config("template_config.json")
    checker_bot = CheckerBot(checker)
    article_iterator = ArticleIterator(
        category_callback=checker_bot.cb_store_category_result,
        article_callback=checker_bot.cb_check_article,
        categories=pagelister.get_county_categories()
    )
    parser = ArticleIteratorArgumentParser(article_iterator, pagelister)
    for argument in pywikibot.handle_args(args):
        if parser.check_argument(argument):
            continue
        elif argument.find("-outputpage:") == 0:
            outputpage = argument[12:]

    article_iterator.iterate_categories()

    result_page = checker_bot.generate_result_page(pagelister)
    result_page += "== Zulässige Vorlagen ==\nDie Seiten wurden mit folgenden zulässigen Vorlagen und Einstellungen geprüft:\n"
    result_page += checker_bot.generate_config_table()

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
