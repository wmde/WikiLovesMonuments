# -*- coding: utf-8 -*-
import unittest
import os

from mock import Mock

from wlmbots.lib import commonscat_mapper


class TestCommonscatMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = commonscat_mapper.CommonscatMapper()
        self.mapper.load_mapping(os.path.join(os.path.dirname(os.path.realpath('__file__')), "config/commonscat_mapping.json"))

    def get_mock_template(self, get_value=u""):
        template = Mock()
        param = Mock()
        param.value = get_value
        template.get.return_value = param
        return template

    def test_category_link_mapping(self):
        commonscat = self.mapper.get_commonscat_from_category_links(
            u"Foo [[Kategorie:Liste (Kulturdenkmäler in Berlin)|Liste der Kulturdenkmäler in Berlin]] Bar")
        self.assertEqual(commonscat, u"Category:Cultural heritage monuments in Berlin")

    def test_weblinks_commonscat_template_returns_comonscat_if_exists(self):
        commonscat = self.mapper.get_commonscat_from_weblinks_template(
            u"Foo\n== Weblinks ==\n {{Commonscat|Cultural heritage monuments in Bad Cannstatt|Kulturdenkmale in Bad Cannstatt}}\n Bar")
        self.assertEqual(commonscat, u"Category:Cultural heritage monuments in Bad Cannstatt")

    def test_weblinks_commonscat_template_returns_empty_string_when_weblinks_header_is_missing(self):
        commonscat = self.mapper.get_commonscat_from_weblinks_template(
            u"Foo\n {{Commonscat|Cultural heritage monuments in Bad Cannstatt|Kulturdenkmale in Bad Cannstatt}} \n Bar")
        self.assertEqual(commonscat, "")

    def test_weblinks_commonscat_template_returns_empty_string_when_commonscat_is_missing(self):
        commonscat = self.mapper.get_commonscat_from_weblinks_template(u"Foo\n == Weblinks ==\n[[Some page]] Bar")
        self.assertEqual(commonscat, "")

    def test_weblinks_commonscat_template_picks_the_first_commonscat_entry(self):
        commonscat = self.mapper.get_commonscat_from_weblinks_template(
            u"Foo\n== Weblinks ==\n {{Commonscat|Cultural heritage monuments in Bad Cannstatt|Kulturdenkmale in Bad Cannstatt}} {{Commonscat|Cultural heritage monuments in Bad Wimpfen|Kulturdenkmale in Bad Wimpfen}}  Bar")
        self.assertEqual(commonscat, u"Category:Cultural heritage monuments in Bad Cannstatt")

    def test_weblinks_commonscat_template_ignores_commonscat_entries_before_weblinks_header(self):
        commonscat = self.mapper.get_commonscat_from_weblinks_template(
            u"{{Commonscat|Cultural heritage monuments in Bad Cannstatt|Kulturdenkmale in Bad Cannstatt}} \n== Weblinks ==\n {{Commonscat|Cultural heritage monuments in Bad Wimpfen|Kulturdenkmale in Bad Wimpfen}}\n  Bar")
        self.assertEqual(commonscat, u"Category:Cultural heritage monuments in Bad Wimpfen")

    def test_commonscat_from_table_row_template_returns_commonscat_if_it_is_not_empty(self):
        template = self.get_mock_template(u"Cultural heritage monuments in Berlin")
        commonscat = self.mapper.get_commonscat_from_table_row_template(template)
        template.get.assert_called_once_with("Commonscat")
        self.assertEqual(commonscat, u"Category:Cultural heritage monuments in Berlin")

    def test_commonscat_from_table_row_template_strips_whitespace_from_commonscat(self):
        template = self.get_mock_template(u" Cultural heritage monuments in Berlin   \n")
        commonscat = self.mapper.get_commonscat_from_table_row_template(template)
        template.get.assert_called_once_with("Commonscat")
        self.assertEqual(commonscat, u"Category:Cultural heritage monuments in Berlin")

    def test_commonscat_from_table_row_template_returns_empty_string_if_it_is_empty(self):
        template = self.get_mock_template(u"")
        commonscat = self.mapper.get_commonscat_from_table_row_template(template)
        template.get.assert_called_once_with("Commonscat")
        self.assertEqual(commonscat, u"")

    def test_commonscat_from_table_row_template_returns_empty_string_if_only_whitespace(self):
        template = self.get_mock_template(u"    \n")
        commonscat = self.mapper.get_commonscat_from_table_row_template(template)
        template.get.assert_called_once_with("Commonscat")
        self.assertEqual(commonscat, u"")

    def test_commonscat_from_table_row_template_returns_empty_string_if_template_throws_error(
            self):
        template = Mock()
        template.get.side_effect = ValueError("Commonscat")
        commonscat = self.mapper.get_commonscat_from_table_row_template(template)
        template.get.assert_called_once_with("Commonscat")
        self.assertEqual(commonscat, u"")

    def test_get_commonscat_returns_commonscat_from_template_row_if_it_exists(self):
        template = self.get_mock_template(u"Cultural heritage monuments in Meetschow")
        pagetext = u"Foo\n== Weblinks ==\n{{Commonscat|Cultural heritage monuments in Gorleben|Baudenkmale in Gorleben}}  \n[[Kategorie:Liste (Baudenkmale in Niedersachsen)|Gorleben]] Bar"
        commonscat = self.mapper.get_commonscat(pagetext, template)
        self.assertEqual(commonscat, u"Category:Cultural heritage monuments in Meetschow")

    def test_get_commonscat_returns_commonscat_from_weblinks_if_table_row_is_empty(self):
        template = self.get_mock_template(u"")
        pagetext = u"Foo\n== Weblinks ==\n{{Commonscat|Cultural heritage monuments in Gorleben|Baudenkmale in Gorleben}}  \n[[Kategorie:Liste (Baudenkmale in Niedersachsen)|Gorleben]] Bar"
        commonscat = self.mapper.get_commonscat(pagetext, template)
        self.assertEqual(commonscat, u"Category:Cultural heritage monuments in Gorleben")

    def test_get_commonscat_returns_commonscat_from_category_links_if_row_and_commonscat_template_empty(
            self):
        template = self.get_mock_template(u"")
        pagetext = u"Foo \n[[Kategorie:Liste (Baudenkmale in Niedersachsen)|Gorleben]] Bar"
        commonscat = self.mapper.get_commonscat(pagetext, template)
        self.assertEqual(commonscat, u"Category:Cultural heritage monuments in Lower Saxony")


if __name__ == '__main__':
    unittest.main()
