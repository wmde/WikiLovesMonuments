# -*- coding: utf-8 -*-
import mwparserfromhell


class PageInformation(object):
    """
    Holds information about a page concerning the ID and image found in the page templates.
    """

    def __init__(self):
        self.category = u""
        self.id = u""
        self.has_duplicate_ids = False
        self.id_was_found = False
        self.has_image = False
        self.has_valid_id = False
        self.meta = {}

    @property
    def has_usable_id(self):
        """
        Check if the object has an id and if the id is unique
        :return: bool
        """
        return self.id and not self.has_duplicate_ids


class PageInformationCollector(object):

    def __init__(self, template_checker, commonscat_mapper):
        """
        :param template_checker:
        :type template_checker: wlmbots.lib.template_checker.TemplateChecker
        :param commonscat_mapper:
        :type commonscat_mapper: wlmbots.lib.commonscat_mapper.CommonscatMapper
        """
        self.template_checker = template_checker
        self.commonscat_mapper = commonscat_mapper

    def get_information(self, article, monument_id):
        """
        Create PageInformation instance from data in Wikipedia article.

        :param article: A Wikipedia monument list article
        :type article: pywikibot.Article
        :param monument_id: Monument ID to search for in the article text. Can be empty to
            just fill in the category
        :return: PageInformation
        """
        info = PageInformation()
        if not article.exists():
            info.meta["article_not_found"] = True
            return info
        text = article.get()
        info.category = self.get_most_specific_category(text)
        if not monument_id:
            info.meta["no_monument_id"] = True
            return info
        id_count = 0
        templates = mwparserfromhell.parse(text).filter_templates()
        template_count = 0
        for template in self.template_checker.filter_allowed_templates(templates):
            template_count += 1
            if self.template_checker.get_id(template) != monument_id:
                continue
            if id_count:
                id_count += 1
                continue
            id_count = 1
            info.category = self.get_most_specific_category(text, template)
            info.id = monument_id
            info.has_valid_id = self.template_checker.has_valid_id(template)
            info.has_image = self.image_exists(template)
        info.meta["template_count"] = template_count
        if info.id:
            info.has_duplicate_ids = id_count > 1
        return info

    def get_most_specific_category(self, text, template=None):
        """
        Get the most specific category from various sources.

        The categories are searched fro in the following order:
        1. The Commonscat parameter of the template
        2. The Weblinks section of the text, looking for the "Commonscat" template
        3. The article category, mapping counties

        :param text: article text
        :type text: unicode
        :param template: table row template
        :type template: mwparserfromhell.nodes.Template
        :return:
        """
        try:
            if template:
                return self.commonscat_mapper.get_commonscat(text, template)
            else:
                commonscat_list = self.commonscat_mapper.get_commonscat_list_from_links(text)
                # return first non-empty element or fail
                return next(category for category in commonscat_list if category)
        except StopIteration:
            return ""

    @staticmethod
    def image_exists(template):
        """
        Check if the "Bild" parameter of the template is filled.

        :param template: A table row template
        :type template: mwparserfromhell.nodes.Template
        :return: bool
        """
        try:
            return template.get("Bild").value.strip() != ""
        except ValueError:
            return False
