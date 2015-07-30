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
from wlmbots.lib.campaign_mapper import CampaignMapper
from wlmbots.lib.template_replacer import TemplateReplacer
from wlmbots.lib.pagelist import Pagelist
from wlmbots.lib.article_iterator import ArticleIterator, ArticleIteratorArgumentParser
from wlmbots.lib.template_checker import TemplateChecker


WLM_PLACEHOLDER = '{{LinkToCommons|Campaign=#campaign#|categories=#commonscat#|Lat=|Lon=|ID=#id#}}'

class UpdateBot(object):

    def __init__(self, commonscat_mapper, template_checker, campaign_mapper):
        self.commonscat_mapper = commonscat_mapper
        self.template_checker = template_checker
        self.campaign_mapper = campaign_mapper
        self.current_campaign = None

    def cb_add_placeholders(self, article, **kwargs):
        logging.info("%s", article.title())
        if article.isRedirectPage():
            return
        errors = self.template_checker.check_article_for_errors(article)
        if TemplateChecker.ERROR_MISSING_TEMPLATE in errors:
            logging.info("  No templates found, skipping")
            return
        text = article.get()
        commonscat = self.commonscat_mapper.get_commonscat_from_category_links(text)
        if not commonscat:
            logging.error("  %s has no mapped category link.", article.title())
            return
        text_with_placeholders_in_templates = self.replace_in_templates(text, errors)
        if text != text_with_placeholders_in_templates:
            # TODO store new text
            logging.info("  Updated article with placeholders")
            logging.debug(text_with_placeholders_in_templates)

    def cb_switch_campaign(self, category, **kwargs):
        self.current_campaign = self.campaign_mapper.get_campaign(category.title())

    def replace_in_templates(self, text, errors):
        global WLM_PLACEHOLDER
        code = mwparserfromhell.parse(text)
        for template in self.template_checker.filter_allowed_templates(code.filter_templates()):
            replacer = TemplateReplacer(template)
            if replacer.param_is_empty("Bild"):
                row_commonscat = self.commonscat_mapper.get_commonscat(text, template)
                placeholder = WLM_PLACEHOLDER.replace("#commonscat#", row_commonscat)
                placeholder = placeholder.replace("#campaign#", self.current_campaign)
                placeholder = placeholder.replace("#id#", self._get_id_for_placeholder(template, errors))
                replacer.set_value('Bild', placeholder)
                text = text.replace(unicode(template), unicode(replacer))
        return text


    def _get_id_for_placeholder(self, template, errors):
        placeholder_id = self.template_checker.get_id(template)
        if not placeholder_id:
            return u""
        if TemplateChecker.ERROR_DUPLICATE_IDS in errors and placeholder_id in errors[TemplateChecker.ERROR_DUPLICATE_IDS]:
            return u""
        return placeholder_id


def main(*args):
    utf8_writer = codecs.getwriter('utf8')
    output_destination = utf8_writer(sys.stdout)
    verbosity = logging.ERROR
    site = pywikibot.Site()
    pagelister = Pagelist(site)
    commonscat_mapper = CommonscatMapper()
    commonscat_mapper.load_mapping("config/commonscat_mapping.json")
    commonscat_mapper.load_subcategories_into_map(site)
    checker = TemplateChecker()
    checker.load_config("template_config.json")
    campaign_mapper = CampaignMapper(commonscat_mapper)
    campaign_mapper.load_mapping("config/campaigns.json")
    update_bot = UpdateBot(commonscat_mapper, checker, campaign_mapper)
    article_iterator = ArticleIterator(
        article_callback=update_bot.cb_add_placeholders,
        category_callback=update_bot.cb_switch_campaign,
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
