# -*- coding: utf-8 -*-

import re

class AllowedTemplates(object):
    """ Stores the configured template names and allowed ID patterns """

    config = {
        u"Denkmalliste Bayern Tabellenzeile": {
            "id": "Nummer",
            "id_check": re.compile(r"D-\d-\d{3}-\d{3}-\d{3}")
        },
        u"Denkmalliste Brandenburg Tabellenzeile": {
            "id": "ID",
            "id_check": re.compile(r"\d{8}")
        },
        u"Denkmalliste Hamburg Tabellenzeile": {
            "id": "Nummer",
            "id_check": re.compile(r"\d{4,}")
        },
        u"Denkmalliste Hessen Tabellenzeile": {
            "id": "Nummer",
            "id_check": re.compile(r"\d{4,}")
        },
        u"Denkmalliste1 Tabellenzeile": {
            "id": "Nummer",
            "id_check": re.compile(r"\d{4,}")
        },
        u"Denkmalliste Mecklenburg-Vorpommern Tabellenzeile": {
            "id": "ID",
            "id_check": re.compile(r"\d{4,}")
        },
        u"Denkmalliste Sachsen Tabellenzeile": {
            "id": "ID",
            "id_check": re.compile(r"\d{4,}")
        },
        u"Denkmalliste Sachsen-Anhalt Tabellenzeile": {
            "id": "ID",
            "id_check": re.compile(r"\d{8}")
        },
        u"Denkmalliste Thüringen Tabellenzeile": {
            "id": "ID",
            "id_check": re.compile(r"\d{4,}")
        },
    }

    def __init__(self):
        self.tpl_match_regex = None

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
