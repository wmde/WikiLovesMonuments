# -*- coding: utf-8 -*-
import mwparserfromhell
import re
import json
import pywikibot


class CommonscatMapper(object):
    mapping = {}

    def __init__(self):
        self.category_cache = {}
        self.subcategories_loaded = False
        self.category_prefix_regex = re.compile(r"^(Category|Kategorie):")

    def load_subcategories_into_map(self, site):
        if self.subcategories_loaded:
            return
        for category_name in self.mapping.copy():
            category = pywikibot.Category(site, category_name)
            for subcategory in category.subcategories():
                self._add_category_to_mapping(subcategory, self.mapping[category_name])
        self.subcategories_loaded = True


    def _add_category_to_mapping(self, category, commonscat):
        self.mapping[category.title()] = commonscat
        for subcategory in category.subcategories():
            self._add_category_to_mapping(subcategory, commonscat)


    def load_mapping(self, filename):
        with open(filename, "r") as mapconf:
            self.mapping = json.load(mapconf)

    def get_commonscat_from_category_links(self, text):
        """ Get the commonscat from the Category links (which is guaranteed to
            be on every page of the WLM pages)
        """
        text_id = id(text)
        if text_id in self.category_cache:
            return self.category_cache[text_id][1]
        code = mwparserfromhell.parse(text)
        for link in code.filter_wikilinks():
            title = unicode(link.title)
            if title in self.mapping:
                return self.mapping[title]

    def get_commonscat_from_weblinks_template(self, text):
        header_pos = re.search(r'=+\s+Weblinks', text, re.IGNORECASE)
        if not header_pos:
            return ""
        weblink_text = text[header_pos.start(0):]
        for template in mwparserfromhell.parse(weblink_text).filter_templates():
            if template.name.matches("Commonscat"):
                return u"Category:" + unicode(template.params[0])
        return ""

    def get_commonscat_from_table_row_template(self, template):
        """ Check mwparserfromhell template if it has a non-empty Commonscat parameter. """
        if template.has("Commonscat"):
            return template.get("Commonscat").value.strip()
        else:
            return ""

    def get_commonscat(self, text, template, with_prefix=True):
        text_id = id(text)
        if text_id not in self.category_cache:
            self.category_cache[text_id] = [
                self.get_commonscat_from_weblinks_template(text),
                self.get_commonscat_from_category_links(text)
            ]
        category_candidates = [self.get_commonscat_from_table_row_template(template)] + self.category_cache[text_id]
        category_name = next(category for category in category_candidates if category)  # first non-empyt element
        prefix = self.category_prefix_regex.match(category_name)
        if with_prefix and not prefix:
            return "Category:" + category_name
        elif not with_prefix and prefix:
            return category_name[prefix.end():]
        else:
            return category_name
