# -*- coding: utf-8 -*-
import unittest
import re

from mock import Mock
from wlmbots.lib.template_checker import TemplateChecker


class TestTemplateChecker(unittest.TestCase):

    def setUp(self):
        self.config = {
            u"Denkmalliste Sachsen Tabellenzeile": {
                "id": "ID",
                "id_check": "\\d{4,}",
                "id_check_description": u"Nummer, mindestens vierstellig"
            },
            u"Denkmalliste Bayern Tabellenzeile": {
                "id": "Nummer",
                "id_check": "D-\\d-\\d{3}",
                "id_check_description": u"Nummer im Format D-n-nnn"
            }
        }
        self.checker = TemplateChecker(self.config)

    def create_article_with_text(self, text):
        """ Build an Article fixture """
        article = Mock()
        article.get.return_value = text
        article.isRedirectPage.return_value = False
        return article

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

    def test_check_for_errors_skips_redirect_pages(self):
        article = Mock()
        article.isRedirectPage.return_value = True
        self.assertEqual(None, self.checker.check_article_for_errors(article))

    def test_check_for_errors_reports_pages_without_templates(self):
        article = self.create_article_with_text(u"Just some test text")
        errors = self.checker.check_article_for_errors(article)
        self.assertEqual({TemplateChecker.ERROR_MISSING_TEMPLATE: True}, errors)

    def test_check_for_errors_reports_invalid_ids(self):
        article = self.create_article_with_text(u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}")
        errors = self.checker.check_article_for_errors(article)
        self.assertEqual({TemplateChecker.ERROR_INVALID_IDS: 1}, errors)

    def test_check_for_errors_returns_empty_dict_for_valid_text(self):
        article = self.create_article_with_text(u"{{Denkmalliste Sachsen Tabellenzeile|ID=1234}}")
        errors = self.checker.check_article_for_errors(article)
        self.assertEqual({}, errors)

    def test_check_for_errors_reports_duplicate_ids(self):
        article = self.create_article_with_text(
            u"{{Denkmalliste Sachsen Tabellenzeile|ID=1234}}{{Denkmalliste Sachsen Tabellenzeile|ID=1234}}{{Denkmalliste Sachsen Tabellenzeile|ID=1223}}")
        errors = self.checker.check_article_for_errors(article)
        self.assertEqual({TemplateChecker.ERROR_DUPLICATE_IDS: {u"1234": 2}}, errors)

    def test_check_for_errors_can_report_multiple_errors(self):
        article = self.create_article_with_text(
            u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}{{Denkmalliste Sachsen Tabellenzeile|ID=1}}{{Denkmalliste Sachsen Tabellenzeile|}}")
        errors = self.checker.check_article_for_errors(article)
        expected_errors = {
            TemplateChecker.ERROR_INVALID_IDS: 2,
            TemplateChecker.ERROR_MISSING_IDS: 1,
            TemplateChecker.ERROR_DUPLICATE_IDS: {u"1": 2}
        }
        self.assertEqual(expected_errors, errors)


if __name__ == '__main__':
    unittest.main()
