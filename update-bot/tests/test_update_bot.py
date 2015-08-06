# -*- coding: utf-8 -*-
import unittest

from mock import Mock  # unittest.mock for Python >= 3.3

from wlmbots import update_bot
from wlmbots.lib.template_checker import TemplateChecker

class TestUpdateBot(unittest.TestCase):

    def setUp(self):
        self.template_checker = TemplateChecker({
            "Denkmalliste Bayern Tabellenzeile": {
                "id": "Nummer",
                "id_check": "D-\\d-\\d{3}-\\d{3}-\\d{3}",
            }
        })
        self.commonscat_mapper = Mock()
        self.bot = update_bot.UpdateBot(self.commonscat_mapper, self.template_checker)

    def test_existing_commonscat_is_preserved(self):
        article_text = u"{{Denkmalliste Bayern Tabellenzeile|Bild=Kruzifix.jpg|Commonscat=testcategory}}"
        new_text = self.bot.replace_in_templates(article_text, u"New Category")
        self.assertEqual(new_text, article_text)

    def test_missing_commonscat_is_added(self):
        article_text = u"{{Denkmalliste Bayern Tabellenzeile|Bild=Kruzifix.jpg|Commonscat=\n}}"
        self.commonscat_mapper.get_commonscat.return_value = "testcategory"
        new_text = self.bot.replace_in_templates(article_text, "Unspecific Category")
        self.assertEqual(new_text, "{{Denkmalliste Bayern Tabellenzeile|Bild=Kruzifix.jpg|Commonscat=testcategory\n}}")


if __name__ == '__main__':
    unittest.main()
