# -*- coding: utf-8 -*-
import unittest

from mock import Mock

from wlmbots import checker_bot
from wlmbots.lib import template_checker


class TestCheckerBot( unittest.TestCase ):
    """ Integration testing for checker_bot """


    def setUp( self ):
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
        self.checker = template_checker.TemplateChecker( self.config )


    def create_article_with_text( self, text ):
        article = Mock( )
        article.get.return_value = text
        article.isRedirectPage.return_value = False
        return article


    def test_check_for_errors_skips_redirect_pages( self ):
        article = Mock( )
        article.isRedirectPage.return_value = True
        self.assertEqual( None, checker_bot.check_for_errors( article, self.checker ) )


    def test_check_for_errors_reports_pages_without_templates( self ):
        article = self.create_article_with_text( u"Just some test text" )
        errors = checker_bot.check_for_errors( article, self.checker )
        self.assertEqual( { checker_bot.ERROR_MISSING_TEMPLATE: True }, errors )


    def test_check_for_errors_reports_invalid_ids( self ):
        article = self.create_article_with_text( u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}" )
        errors = checker_bot.check_for_errors( article, self.checker )
        self.assertEqual( { checker_bot.ERROR_INVALID_IDS: 1 }, errors )


    def test_check_for_errors_returns_empty_dict_for_valid_text( self ):
        article = self.create_article_with_text( u"{{Denkmalliste Sachsen Tabellenzeile|ID=1234}}" )
        errors = checker_bot.check_for_errors( article, self.checker )
        self.assertEqual( { }, errors )


    def test_check_for_errors_reports_duplicate_ids( self ):
        article = self.create_article_with_text(
            u"{{Denkmalliste Sachsen Tabellenzeile|ID=1234}}{{Denkmalliste Sachsen Tabellenzeile|ID=1234}}{{Denkmalliste Sachsen Tabellenzeile|ID=1223}}" )
        errors = checker_bot.check_for_errors( article, self.checker )
        self.assertEqual( { checker_bot.ERROR_DUPLICATE_IDS: { u"1234": 2 } }, errors )


    def test_check_for_errors_can_report_multiple_errors( self ):
        article = self.create_article_with_text(
            u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}{{Denkmalliste Sachsen Tabellenzeile|ID=1}}{{Denkmalliste Sachsen Tabellenzeile|}}" )
        errors = checker_bot.check_for_errors( article, self.checker )
        expected_errors = {
            checker_bot.ERROR_INVALID_IDS: 2,
            checker_bot.ERROR_MISSING_IDS: 1,
            checker_bot.ERROR_DUPLICATE_IDS: { u"1": 2 }
        }
        self.assertEqual( expected_errors, errors )


    def test_generate_config_table_contains_a_column_for_each_template_configuration_in_alphabetic_order_of_template_names(
            self ):
        config_table = checker_bot.generate_config_table( self.config )
        config_table_lines = config_table.split( "|-\n" )
        self.assertIn( "|[[Vorlage:Denkmalliste Bayern Tabellenzeile", config_table_lines[2] )
        self.assertIn( "|[[Vorlage:Denkmalliste Sachsen Tabellenzeile", config_table_lines[3] )


    def test_generate_config_table_contains_a_column_id( self ):
        config_table = checker_bot.generate_config_table( self.config )
        config_table_lines = config_table.split( "|-\n" )
        self.assertIn( "|Nummer", config_table_lines[2] )
        self.assertIn( "|ID", config_table_lines[3] )


    def test_generate_config_table_contains_a_description_of_valid_ids( self ):
        config_table = checker_bot.generate_config_table( self.config )
        config_table_lines = config_table.split( "|-\n" )
        self.assertIn( "|Nummer im Format D-n-nnn", config_table_lines[2] )
        self.assertIn( "|Nummer, mindestens vierstellig", config_table_lines[3] )


        # TODO write tests for generate_result_page and get_results_for_county


if __name__ == '__main__':
    unittest.main( )
