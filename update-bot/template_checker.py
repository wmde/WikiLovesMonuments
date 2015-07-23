# -*- coding: utf-8 -*-

import re
import json

class TemplateChecker(object):
    """ Stores the configured template names and allowed ID patterns """

    def __init__(self, config={}):
        self.tpl_match_regex = None
        self.config = config

    def text_contains_templates(self, text):
        if not self.tpl_match_regex:
            pattern = r"\{\{" + "|".join([re.escape(tpl) for tpl in self.config])
            self.tpl_match_regex = re.compile(pattern)
        return bool(self.tpl_match_regex.search(text))

    def get_id(self, template):
        id_name = self.config[template.name]["id"]
        try:
            id_param = unicode(template.get(id_name)).strip()
            if not id_param:
                return ""
            _, id_value = id_param.split("=", 1)
            return id_value.strip()
        except ValueError as e:
            if str(e) == id_name:
                return ""
            else:
                raise

    def has_valid_id(self, template):
        return bool(self.config[template.name]["id_check"].search(self.get_id(template)))

    def compile_id_check_patterns(self, config):
        retype = type(re.compile("test"))
        for tpl in config:
            if "id_check" in config[tpl] and not isinstance(config[tpl]["id_check"], retype):
                config[tpl]["id_check"] = re.compile(config[tpl]["id_check"])
        return config

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._config = self.compile_id_check_patterns(config)
        self.tpl_match_regex = None
