# -*- coding: utf-8 -*-
import unittest
from mock import Mock

from template_checker import TemplateChecker

class TestTemplateChecker(unittest.TestCase):

    def setUp(self):
        self.checker = TemplateChecker()

    def test_text_contains_templates_finds_template_name(self):
        text = "{{Denkmalliste Bayern Tabellenzeile|}}"
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

if __name__ == '__main__':
    unittest.main()
