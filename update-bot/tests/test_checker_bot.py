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


    def test_generate_config_table_contains_template_configuration_columns_in_alphabetic_order(
            self):
        config_table = checker_bot.generate_config_table(self.config)
        config_table_lines = config_table.split("|-\n")
        self.assertIn("|[[Vorlage:Denkmalliste Bayern Tabellenzeile", config_table_lines[2])
        self.assertIn("|[[Vorlage:Denkmalliste Sachsen Tabellenzeile", config_table_lines[3])


    def test_generate_config_table_contains_a_column_id(self):
        config_table = checker_bot.generate_config_table(self.config)
        config_table_lines = config_table.split("|-\n")
        self.assertIn("|Nummer", config_table_lines[2])
        self.assertIn("|ID", config_table_lines[3])


    def test_generate_config_table_contains_a_description_of_valid_ids(self):
        config_table = checker_bot.generate_config_table(self.config)
        config_table_lines = config_table.split("|-\n")
        self.assertIn("|Nummer im Format D-n-nnn", config_table_lines[2])
        self.assertIn("|Nummer, mindestens vierstellig", config_table_lines[3])

        # TODO write tests for generate_result_page and get_results_for_county

if __name__ == '__main__':
    unittest.main()
