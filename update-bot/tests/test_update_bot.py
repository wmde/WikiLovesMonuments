# -*- coding: utf-8 -*-
import unittest

from mock import Mock  # unittest.mock for Python >= 3.3

from wlmbots import update_bot
from wlmbots.lib.commonscat_mapper import CommonscatMapper
from wlmbots.lib.template_checker import TemplateChecker

class TestUpdateBot(unittest.TestCase):

    def setUp(self):
        self.template_checker = TemplateChecker({
            "Denkmalliste Bayern Tabellenzeile": {
                "id": "Nummer",
                "id_check": "D-\\d-\\d{3}-\\d{3}-\\d{3}",
            }
        })
        self.bot = update_bot.UpdateBot(CommonscatMapper(), self.template_checker)

    def test_replace_in_templates_does_nothing_if_image_exists(self):
        article_text = "{{Denkmalliste Bayern Tabellenzeile|Bild=Kruzifix.jpg|Commonscat=testcategory}}"
        new_text = self.bot.replace_in_templates(article_text, {})
        self.assertEqual(new_text, article_text)

    def test_replace_in_templates_inserts_placeholder_when_image_is_missing(self):
        article_text = "{{Denkmalliste Bayern Tabellenzeile|Bild=|Commonscat=testcategory}}"
        update_bot.WLM_PLACEHOLDER = "<-- test placeholder -->"
        new_text = self.bot.replace_in_templates(article_text, {})
        self.assertEqual(new_text,
                         "{{Denkmalliste Bayern Tabellenzeile|Bild=<-- test placeholder -->|Commonscat=testcategory}}")

    def test_replace_in_templates_inserts_commoncat_in_placeholder(self):
        article_text = "{{Denkmalliste Bayern Tabellenzeile|Bild=\n|Commonscat=testcategory\n}}"
        update_bot.WLM_PLACEHOLDER = "<-- #commonscat# -->"
        new_text = self.bot.replace_in_templates(article_text, {})
        self.assertEqual(new_text,
                         "{{Denkmalliste Bayern Tabellenzeile|Bild=<-- Category:testcategory -->\n|Commonscat=testcategory\n}}")

    def test_add_placeholders_does_nothing_if_category_link_is_missing(self):
        article = Mock()
        article.get.return_value = "{{Denkmalliste Bayern Tabellenzeile|Bild=}}"
        article.title.return_value = "Testseite"
        self.bot.cb_add_placeholders(article)
        article.save.assert_not_called()


if __name__ == '__main__':
    unittest.main()
