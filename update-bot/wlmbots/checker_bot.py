#!/usr/bin/python
# -*- coding: utf-8 -*-
""" This bot checks the pages in the "Denkmalliste" categories for templates
    and unique IDs. It can create a result page from the check or just
    output the result.

Available command line options are:

-limit:N          Only check N number of pages

-limit-per-category:N Only check N number of pages per category

-category:NAME    Only check pages in category NAME

-outputpage:NAME  Write result to wiki page NAME instead of stdout

-exclude-articles:NAME Ignore all pages that are linked to on page NAME

"""

from __future__ import unicode_literals

import tempfile
from string import Template

import pywikibot
import mwparserfromhell

from wlmbots.lib.template_checker import TemplateChecker
from wlmbots.lib.category_fetcher import CategoryFetcher
from wlmbots.lib.article_iterator import ArticleIterator, ArticleIteratorArgumentParser, ArticleIteratorCallbacks


class CheckerBot(object):

    def __init__(self, template_checker, site):
        self.results = []
        self.article_results = []
        self.previous_count = 0
        self.checker = template_checker
        self.site = site
        self.outputpage = None

    def generate_summary_page(self):
        text = u"\n"
        if self.outputpage:
            template = Template(u"; [[$outputpage/$category_title|$category_title]]\n: $result_summary")
        else:
            template = Template(u"[[$category_title]]\n$result_summary")
        for category_results in self.results:
            _, category_title = category_results["category"].title().split(":", 1)
            text += template.substitute(outputpage=self.outputpage, category_title=category_title,
                                        result_summary=self.get_result_summary(category_results))
        return text

    def generate_category_result_header(self, results, pagelister=None):
        text = u""
        heading = "=="
        category = results["category"]
        if not pagelister:
            pagelister = CategoryFetcher(self.site)
        if pagelister.root_category not in category.categories():
            heading += "="
        text += u"\n{} {} {}\n".format(heading, category.title(), heading)
        text += self.get_result_summary(results)
        return text

    def get_result_summary(self, results):
        text = u""
        if results["pages_checked"] == 0:
            return text + "Es wurden keine Seiten in dieser Kategorie geprüft.\n"
        unsupported, partially_supported = self.count_error_types(results["results"])
        num_errors = unsupported + partially_supported
        pages_ok = results["pages_checked"] - num_errors
        text += u"{} {} geprüft".format(results["pages_checked"], self._plural_pages(results["pages_checked"]))
        if num_errors == 0:
            text += u", alle Seiten werden unterstützt"
        elif unsupported == results["pages_checked"]:
            text += u", keine der Seiten wird unterstützt"
        elif partially_supported == results["pages_checked"]:
            text += u", alle Seiten werden nur teilweise unterstützt"
        else:
            divisor = float(results["pages_checked"])
            if pages_ok == 0:
                text += u", keine der Seiten voll unterstützt"
            else:
                text += u", {} {} unterstützt ({:.0%})".format(
                    pages_ok, self._plural_pages(pages_ok), pages_ok / divisor
                )
            if partially_supported > 0:
                text += u", {} {} teilweise unterstützt ({:.0%})".format(
                    partially_supported, self._plural_pages(partially_supported), partially_supported / divisor
                )
            if unsupported > 0:
                text += u", {} {} nicht unterstützt ({:.0%})".format(
                    unsupported, self._plural_pages(unsupported), unsupported / divisor
                )
        text += ".\n"
        return text

    def count_error_types(self, results):
        unsupported = 0
        partially_supported = 0
        for result in results:
            if TemplateChecker.ERROR_MISSING_TEMPLATE in result["errors"]:
                unsupported += 1
            else:
                partially_supported += 1
        return unsupported, partially_supported

    def _plural_pages(self, num_pages):
        if num_pages == 1:
            return u"Seite"
        return u"Seiten"

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
        text = "== Unterstützte Vorlagen ==\nDie Seiten wurden mit folgenden Vorlagen und Einstellungen geprüft:\n"
        text += '{| class="wikitable"\n|-\n!Vorlage!!Bezeichner ID!!Format ID\n'
        for template_name, config in sorted(self.checker.config.items()):
            text += line_fmt.format(template_name, template_name, config["id"], config["id_check_description"])
        text += "|}\n\n"
        return text

    def save_wikipage(self, page_text, page_name, summary="Bot: Update der Ergebnisliste"):
        try:
            article = pywikibot.Page(self.site, page_name)
            if not article.exists() or article.get() != page_text:
                article.text = page_text
                article.save(summary=summary)
            else:
                pywikibot.log("Result page has not changed, skipping update ...")
        except pywikibot.Error:
            with tempfile.NamedTemporaryFile(delete=False) as dump_file:
                dump_file.write(page_name.encode('utf-8'))
                pywikibot.error("Could not update result page, page dumped to {}".format(dump_file.name), exc_info=True)

    def cb_store_category_result(self, category, counter=0, **kwargs):
        category_results = {
            "category": category,
            "results": self.article_results,
            "pages_checked": counter - self.previous_count
        }
        text = self.generate_category_result_header(category_results)
        text += self.generate_category_result_table(category_results)
        if self.outputpage:
            text += self.generate_config_table()
            _, category_title = category.title().split(":", 1)
            page_name = self.outputpage + "/" + category_title
            self.save_wikipage(text, page_name)
        else:
            pywikibot.output(text)
        if self.article_results:
            self.results.append(category_results)
        self.article_results = []
        self.previous_count = counter

    def cb_check_article(self, article, **kwargs):
        errors = self.checker.check_article_for_errors(article)
        if errors:
            self.article_results.append({
                "title": article.title(),
                "errors": errors
            })


def load_excluded_articles_from_wiki(page):
    if not page.exists():
        return []
    text = page.get()
    code = mwparserfromhell.parse(text)
    return [unicode(link.title) for link in code.filter_wikilinks()]

def main(*args):
    site = pywikibot.Site()
    fetcher = CategoryFetcher(site)
    checker = TemplateChecker()
    checker.load_config("config/templates.json")
    checker_bot = CheckerBot(checker, site)
    all_categories = fetcher.get_categories()
    callbacks = ArticleIteratorCallbacks(
        category_callback=checker_bot.cb_store_category_result,
        article_callback=checker_bot.cb_check_article,
        logging_callback=pywikibot.log,
    )
    article_iterator = ArticleIterator(callbacks, categories=all_categories)
    parser = ArticleIteratorArgumentParser(article_iterator, fetcher)
    for argument in pywikibot.handle_args(list(args)):
        if parser.check_argument(argument):
            continue
        elif argument.find("-outputpage:") == 0:
            checker_bot.outputpage = argument[12:]
        elif argument.find("-exclude-articles:") == 0:
            page = pywikibot.Page(site, argument[18:])
            article_iterator.excluded_articles = load_excluded_articles_from_wiki(page)
    article_iterator.iterate_categories()

    if article_iterator.categories != all_categories:   # Don't update summary page if only single categories were crawled
        return
    summary = checker_bot.generate_summary_page()
    if checker_bot.outputpage:
        checker_bot.save_wikipage(summary, checker_bot.outputpage + u"/Zusammenfassung")
    else:
        pywikibot.output(u"Zusammenfassung")
        pywikibot.output(u"===============")
        pywikibot.output(summary)
        pywikibot.output(checker_bot.generate_config_table())


if __name__ == "__main__":
    main()
