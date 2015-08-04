# -*- coding: utf-8 -*-
import unittest

from mock import Mock  # unittest.mock for Python >= 3.3

from wlmbots import update_bot


class TestUpdateBot(unittest.TestCase):
    def test_replace_in_templates_does_nothing_if_image_exists(self):
        article_text = "{{Denkmalliste Bayern Tabellenzeile|Bild=Kruzifix.jpg|Commonscat=testcategory}}"
        new_text = update_bot.replace_in_templates(article_text)
        self.assertEqual(new_text, article_text)

    def test_replace_in_templates_inserts_placeholder_when_image_is_missing(self):
        article_text = "{{Denkmalliste Bayern Tabellenzeile|Bild=|Commonscat=testcategory}}"
        update_bot.WLM_PLACEHOLDER = "<-- test placeholder -->"
        new_text = update_bot.replace_in_templates(article_text)
        self.assertEqual(new_text,
                         "{{Denkmalliste Bayern Tabellenzeile|Bild=<-- test placeholder -->|Commonscat=testcategory}}")

    def test_replace_in_templates_inserts_commoncat_in_placeholder(self):
        article_text = "{{Denkmalliste Bayern Tabellenzeile|Bild=\n|Commonscat=testcategory\n}}"
        update_bot.WLM_PLACEHOLDER = "<-- #commonscat# -->"
        new_text = update_bot.replace_in_templates(article_text)
        self.assertEqual(new_text,
                         "{{Denkmalliste Bayern Tabellenzeile|Bild=<-- Category:testcategory -->\n|Commonscat=testcategory\n}}")

    def test_add_placeholders_does_nothing_if_category_link_is_missing(self):
        article = Mock()
        article.get.return_value = u"{{Denkmalliste Bayern Tabellenzeile|Bild=}}"
        article.title.return_value = "Testseite"
        update_bot.cb_add_placeholders(article)
        article.save.assert_not_called()


if __name__ == '__main__':
    unittest.main()
