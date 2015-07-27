#!/usr/bin/python
# -*- coding: utf-8 -*-
# This bot checks which templates are used on the wlm pages

from __future__ import unicode_literals

import codecs
import sys
import random
import collections

import pywikibot
import mwparserfromhell

from lib.pagelist import Pagelist


class TemplateCounter(object):
    """ Count occurrence of template names on pages """

    ignored_categories = [
        'Coordinate',
        'Internetquelle',
        'Hauptartikel',
        'Commons',
        'Literatur',
        'Rechtshinweis',
        'All Coordinates',
        'Anker',
        'SortKey',
        'commonscat',
        'Commonscat',
        '0',
        '"'
    ]


    def __init__(self):
        self.templates = collections.Counter()


    def count_templates(self, pagetext):
        """ Count templates on a single page """
        code = mwparserfromhell.parse(pagetext)
        for template in code.filter_templates():
            tpl_name = unicode(template.name).strip()
            if tpl_name in self.ignored_categories:
                continue
            self.templates[tpl_name] += 1


class StatsOutput(object):
    """ Output statistics on templates and table headings """


    def __init__(self, output_destination, output_sample_article_titles=False, cutoff=0):
        self.out = output_destination
        self.sample_articles = []
        self.cutoff = cutoff
        self.output_sample_article_titles = output_sample_article_titles


    def add_article(self, article):
        self.sample_articles.append(article)


    def output_result(self, county_name, template_counts, num_articles):
        sample_size = len(self.sample_articles)
        heading = "{} (sampled {} of {} articles)".format(county_name, sample_size, num_articles)
        self.out.write(heading)
        self.out.write("\n")
        self.out.write("=" * len(heading))
        self.out.write("\n")
        if self.output_sample_article_titles:
            self.out.write("Sampled article names:\n")
            self.out.write("\n".join(self.sample_articles))
            self.out.write("\n")
        for item, count in template_counts.most_common():
            if count > self.cutoff:
                self.out.write("{}: {}\n".format(item, count))
        self.out.write("\n")


def sample_county(county, sample_size, output_destination, output_sample_article_titles=False):
    """ Collect samples for one county category and print them """
    articles = list(county.articles())
    if len(articles) > sample_size:
        sample_articles = random.sample(articles, sample_size)
    else:
        sample_articles = articles
    cutoff = 10  # Minimum occurrance of template/table heading to be relevant
    counter_tpl = TemplateCounter()
    output = StatsOutput(output_destination, output_sample_article_titles, cutoff)
    for article in sample_articles:
        if article.isRedirectPage():
            continue
        output.add_article(article.title())
        counter_tpl.count_templates(article.get())
    output.output_result(county.title(), counter_tpl.templates, len(articles))


def main(*args):
    UTF8Writer = codecs.getwriter('utf8')
    output_destination = UTF8Writer(sys.stdout)
    sample_size = 100
    output_sample_article_titles = True

    site = pywikibot.Site()
    lister = Pagelist(site)
    counties = lister.get_county_categories()
    for county in counties:
        sample_county(county, sample_size, output_destination)


if __name__ == "__main__":
    main()
