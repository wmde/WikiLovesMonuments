# -*- coding: utf-8 -*-
"""
Contains the class TemplateChecker that checks templates and articles for errors.
"""

import re
import json
import itertools
import collections
import mwparserfromhell


class TemplateChecker(object):
    """ Check templates for allowed ID patterns """

    ERROR_MISSING_TEMPLATE = 1
    ERROR_TOO_MANY_TEMPLATES = 2
    ERROR_MISSING_IDS = 4
    ERROR_INVALID_IDS = 8
    ERROR_DUPLICATE_IDS = 16

    # How many templates on a page are ok. If more templates are on the page,
    # the Bilderwunsch/ListeneintragWLM template may break the text expansion limit
    # See https://de.wikipedia.org/wiki/Hilfe:Vorlagenbeschr%C3%A4nkungen
    TEMPLATE_LIMIT = 350

    def __init__(self, config=None):
        self._config = {}
        if config:
            self.config = config
        self.tpl_match_regex = None

    def load_config(self, filename):
        """ Load configuration from JSON file """
        with open(filename, "r") as tplconf:
            self.config = json.load(tplconf)

    def text_contains_templates(self, text):
        """
        Check if the page text contains templates that are configured.

        Parameters:
            text - unicode page text

        Returns:
            True if at least one of the configured templates is contained on the
            page, otherwise false.
        """
        if not self.tpl_match_regex:
            pattern = r"\{\{" + "|".join([re.escape(tpl) for tpl in self.config])
            self.tpl_match_regex = re.compile(pattern)
        return bool(self.tpl_match_regex.search(text))

    def get_id(self, template):
        """
        Return unique identifier from template, if it exists.

        Which template param is used for the id ("ID", "Nummer", etc) comes from
        the configuration

        Parameters:
            template - a mwparserfromhell template

        Returns:
            Unique ID or empty string.
        """
        id_name = self.get_id_name(template)
        try:
            id_param = unicode(template.get(id_name)).strip()
            if not id_param:
                return ""
            _, id_value = id_param.split("=", 1)
            return id_value.strip()
        except ValueError as error:
            if str(error) == id_name:
                return ""
            else:
                raise

    def get_id_name(self, template):
        return self.template_config(template)["id"]

    def has_valid_id(self, template):
        """
        Check if the id from the template matches the configured pattern for valid IDs.

        Parameters:
            template - a mwparserfromhell template

        Returns:
            True if ID matches the validation pattern
        """
        return bool(self.template_config(template)["id_check"].search(self.get_id(template)))

    def check_article_for_errors(self, article):
        """
        Return error codes and error meta data for an article.

        Parameters:
            article - a pywikibot Article

        Returns:
            A dictionary with error types as keys and metadata as values.
            If an error type did not occur, it won't be in the dictionary.
            ERROR_MISSING_IDS and ERROR_INVALID_IDS have a value of the number
            of templates where this error occured.
            ERROR_DUPLICATE_IDS has a value list of the duplicate IDs.
            ERROR_MISSING_TEMPLATE is just True or missing in the dict.
        """
        if article.isRedirectPage():
            return
        text = article.get()
        if not self.text_contains_templates(text):
            return {self.ERROR_MISSING_TEMPLATE: True}
        templates = mwparserfromhell.parse(text).filter_templates()
        errors = {
            self.ERROR_MISSING_IDS: 0,
            self.ERROR_INVALID_IDS: 0
        }
        ids = collections.Counter()
        template_count = 0
        for template in self.filter_allowed_templates(templates):
            row_id = self.get_id(template)
            template_count += 1
            if not row_id:
                errors[self.ERROR_MISSING_IDS] += 1
                continue
            ids[row_id] += 1
            if not self.has_valid_id(template):
                errors[self.ERROR_INVALID_IDS] += 1
        errors[self.ERROR_DUPLICATE_IDS] = {row_id: count for row_id, count in ids.iteritems() if count > 1}
        if template_count > self.TEMPLATE_LIMIT:
            errors[self.ERROR_TOO_MANY_TEMPLATES] = template_count
        errors = {e: v for e, v in errors.iteritems() if v}
        return errors

    def filter_allowed_templates(self, templates):
        return itertools.ifilter(self.is_allowed_template, templates)

    def is_allowed_template(self, template):
        return self._get_template_name(template) in self.config

    def compile_id_check_patterns(self, config):
        """ Convert ID patterns in template configuration into compiled regular expression objects. """
        retype = type(re.compile("test"))
        for tpl in config:
            if "id_check" in config[tpl] and not isinstance(config[tpl]["id_check"], retype):
                config[tpl]["id_check"] = re.compile(config[tpl]["id_check"])
        return config

    @staticmethod
    def _normalize_config_names(config):
        """ Replace underscores in template names with spaces """
        new_config = {}
        for template_name in config:
            new_config[template_name.replace("_", " ")] = config[template_name]
        return new_config

    def template_config(self, template):
        """
        Access the template configuration with a template object
        """
        return self.config[self._get_template_name(template)]

    def _get_template_name(self, template):
        return unicode(template.name).strip().replace("_", " ")

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        config = self._normalize_config_names(config)
        self._config = self.compile_id_check_patterns(config)
        self.tpl_match_regex = None
