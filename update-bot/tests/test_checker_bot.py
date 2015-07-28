# -*- coding: utf-8 -*-
import unittest

from mock import Mock

from wlmbots import checker_bot
from wlmbots.lib import template_checker


class TestCheckerBot(unittest.TestCase):
    """ Integration testing for checker_bot """


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
        self.bot = checker_bot.CheckerBot(self.checker)


    def test_generate_config_table_contains_template_configuration_columns_in_alphabetic_order(
            self):
        config_table = self.bot.generate_config_table()
        config_table_lines = config_table.split("|-\n")
        self.assertIn("|[[Vorlage:Denkmalliste Bayern Tabellenzeile", config_table_lines[2])
        self.assertIn("|[[Vorlage:Denkmalliste Sachsen Tabellenzeile", config_table_lines[3])


    def test_generate_config_table_contains_a_column_id(self):
        config_table = self.bot.generate_config_table()
        config_table_lines = config_table.split("|-\n")
        self.assertIn("|Nummer", config_table_lines[2])
        self.assertIn("|ID", config_table_lines[3])


    def test_generate_config_table_contains_a_description_of_valid_ids(self):
        config_table = self.bot.generate_config_table()
        config_table_lines = config_table.split("|-\n")
        self.assertIn("|Nummer im Format D-n-nnn", config_table_lines[2])
        self.assertIn("|Nummer, mindestens vierstellig", config_table_lines[3])


    def test_generate_category_result_header_adds_category_name_as_header(self):
        category = Mock()
        category.categories.return_value = [u"Denkmäler in Deutschland"]
        category.title.return_value = u"Baudenkmäler in Sachsen"
        pagelister = Mock()
        pagelister.root_category = u"Denkmäler in Deutschland"
        results = {
            "category": category,
            "results": [],
            "pages_checked": 0
        }
        header = checker_bot.generate_category_result_header(results, pagelister)
        self.assertIn(u"== Baudenkmäler in Sachsen ==", header)

    def test_generate_category_result_header_increases_header_level_by_one_if_parent_category_is_not_root_category(self):
        category = Mock()
        category.categories.return_value = [u"Denkmäler in Sachsen"]
        category.title.return_value = u"Baudenkmäler in Greifswald"
        pagelister = Mock()
        pagelister.root_category = u"Denkmäler in Deutschland"
        results = {
            "category": category,
            "results": [],
            "pages_checked": 0
        }
        header = checker_bot.generate_category_result_header(results, pagelister)
        self.assertIn(u"=== Baudenkmäler in Greifswald ===", header)

    def test_generate_category_result_header_adds_page_statistics(self):
        category = Mock()
        category.categories.return_value = [u"Denkmäler in Deutschland"]
        category.title.return_value = u"Baudenkmäler in Sachsen"
        pagelister = Mock()
        pagelister.root_category = u"Denkmäler in Deutschland"
        results = {
            "category": category,
            "results": [{}, {}, {}],
            "pages_checked": 100
        }
        header = checker_bot.generate_category_result_header(results, pagelister)
        self.assertIn(u"100 Seiten geprüft", header)
        self.assertIn(u"97 ohne Probleme", header)

    def test_generate_category_result_table_creates_id_template_entries(self):
        results = {
            "results": [
                 {
                    "title" : u"Liste der Baudenkmale in Döbeln",
                    "errors": {
                        checker_bot.ERROR_INVALID_IDS: 7,
                        checker_bot.ERROR_DUPLICATE_IDS: [u"42", u"23"],
                        checker_bot.ERROR_MISSING_IDS: 8
                    }
                }
            ]
        }
        table = checker_bot.generate_category_result_table(results)
        self.assertIn(u"{{Fehler in Denkmallisten Tabellenzeile|", table)
        self.assertIn(u"Titel=Liste der Baudenkmale in Döbeln", table)
        self.assertIn(u"Kein_Template=|", table)
        self.assertIn(u"IDs_fehlen=8", table)
        self.assertIn(u"IDs_ungueltig=7", table)
        self.assertIn(u"IDs_doppelt=42, 23", table)

    def test_generate_category_result_table_creates_missing_template_entries(self):
        results = {
            "results": [
                 {
                    "title" : u"Liste der Baudenkmale in Döbeln",
                    "errors": {
                        checker_bot.ERROR_MISSING_TEMPLATE: True
                    }
                }
            ]
        }
        table = checker_bot.generate_category_result_table(results)
        self.assertIn(u"{{Fehler in Denkmallisten Tabellenzeile|", table)
        self.assertIn(u"Titel=Liste der Baudenkmale in Döbeln", table)
        self.assertIn(u"Kein_Template=True|", table)
        self.assertIn(u"IDs_fehlen=|", table)
        self.assertIn(u"IDs_ungueltig=|", table)
        self.assertIn(u"IDs_doppelt=|", table)


if __name__ == '__main__':
    unittest.main()
