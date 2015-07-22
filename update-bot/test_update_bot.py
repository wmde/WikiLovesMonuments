# -*- coding: utf-8 -*-
import unittest
from mock import MagicMock # unittest.mock for Python >= 3.3

import update_bot

class TestUpdateBot(unittest.TestCase):

    def test_replace_in_templates_does_nothing_if_image_exists(self):
        article_text = "{{Denkmalliste Bayern Tabellenzeile|Bild=Kruzifix.jpg}}"
        new_text = update_bot.replace_in_templates(article_text, "")
        self.assertEqual(new_text, article_text)

    def test_replace_in_templates_inserts_placeholder_when_image_is_missing(self):
        article_text = "{{Denkmalliste Bayern Tabellenzeile|Bild=}}"
        update_bot.WLM_PLACEHOLDER = "<-- test placeholder -->"
        new_text = update_bot.replace_in_templates(article_text, "")
        self.assertEqual(new_text, "{{Denkmalliste Bayern Tabellenzeile|Bild=<-- test placeholder -->}}")

    def test_replace_in_templates_inserts_commoncat_in_placeholder(self):
        article_text = "{{Denkmalliste Bayern Tabellenzeile|Bild=}}"
        update_bot.WLM_PLACEHOLDER = "<-- #commonscat# -->"
        new_text = update_bot.replace_in_templates(article_text, "testcategory")
        self.assertEqual(new_text, "{{Denkmalliste Bayern Tabellenzeile|Bild=<-- testcategory -->}}")

    def test_add_placeholders_does_nothing_if_category_link_is_missing(self):
        article = MagicMock()
        article.get.return_value = "{{Denkmalliste Bayern Tabellenzeile|Bild=}}"
        article.title.return_value = "Testseite"
        article.save.assert_not_called()
        update_bot.add_placeholders(article)


if __name__ == '__main__':
    unittest.main()
