# -*- coding: utf-8 -*-
import unittest
import re

from mock import Mock
from wlmbots.lib.template_checker import TemplateChecker


class TestTemplateChecker(unittest.TestCase):

    def setUp(self):
        config = {
            "Denkmalliste Sachsen Tabellenzeile": {
                "id": "ID",
                "id_check": "\\d{4,}"
             }
        }
        self.checker = TemplateChecker(config)

    def test_text_contains_templates_finds_template_name(self):
        text = "{{Denkmalliste Sachsen Tabellenzeile|}}"
        self.assertTrue(self.checker.text_contains_templates(text))

    def test_get_id_returns_id(self):
        template = Mock()
        template.get.return_value = u"ID=12345"
        template.name = u"Denkmalliste Sachsen Tabellenzeile"
        self.assertEqual(self.checker.get_id(template), u"12345")

    def test_get_id_returns_empty_string_if_is_empty(self):
        template = Mock()
        template.get.return_value = u"ID="
        template.name = u"Denkmalliste Sachsen Tabellenzeile"
        self.assertEqual(self.checker.get_id(template), u"")

    def test_has_valid_id_true_for_valid_ids(self):
        template = Mock()
        template.get.return_value = u"ID=12345"
        template.name = u"Denkmalliste Sachsen Tabellenzeile"
        self.assertTrue(self.checker.has_valid_id(template))

    def test_has_valid_id_true_for_invalid_ids(self):
        template = Mock()
        template.get.return_value = u"ID=123"
        template.name = u"Denkmalliste Sachsen Tabellenzeile"
        self.assertFalse(self.checker.has_valid_id(template))

    def test_setting_configuration_compiles_regex_patterns(self):
        self.checker.config = {
            "Denkmalliste Bayern Tabellenzeile": {
                "id": "ID",
                "id_check": "D-d{3}"
             }
        }
        expected_class = type(re.compile("test"))
        self.assertIsInstance(self.checker.config["Denkmalliste Bayern Tabellenzeile"]["id_check"], expected_class)

    def test_is_allowed_template_checks_if_template_name_is_configured(self):
        template = Mock()
        template.name = u"Denkmalliste Sachsen Tabellenzeile"
        self.assertTrue(self.checker.is_allowed_template(template))
        template.name = u"Denkmalliste Kleinkleckersdorf Tabellenzeile"
        self.assertFalse(self.checker.is_allowed_template(template))

if __name__ == '__main__':
    unittest.main()
