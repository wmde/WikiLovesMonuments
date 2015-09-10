# -*- coding: utf-8 -*-
import unittest
from mock import Mock

from forward_script.lib.page_information import PageInformation, PageInformationCollector


class TestPageInformation(unittest.TestCase):

    def test_has_usable_id(self):
        page_information = PageInformation()
        self.assertFalse(page_information.has_usable_id)
        page_information.id = "123"
        self.assertTrue(page_information.has_usable_id)
        page_information.has_duplicate_ids = True
        self.assertFalse(page_information.has_usable_id)


class TestPageInformationCollector(unittest.TestCase):

    def setUp(self):
        self.mapper = Mock()
        self.checker = Mock()
        self.collector = PageInformationCollector(self.checker, self.mapper)
        self.article = Mock()

    def test_get_info_returns_no_usable_id_if_id_does_not_match(self):
        self.checker.filter_allowed_templates = Mock(side_effect=lambda x: x)
        self.checker.get_id.return_value = u"1"
        self.mapper.get_commonscat_list_from_links.return_value = [u"Weblink Category"]
        self.article.get.return_value = u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}"
        info = self.collector.get_information(self.article, u"123")
        self.assertFalse(info.has_usable_id)

    def test_get_info_accepts_empty_id(self):
        self.checker.filter_allowed_templates = Mock(side_effect=lambda x: x)
        self.mapper.get_commonscat_list_from_links.return_value = [u"Weblink Category"]
        self.article.get.return_value = u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}"
        info = self.collector.get_information(self.article, u"")
        self.assertFalse(info.has_usable_id)
        self.assertTrue(info.meta["no_monument_id"])

    def test_get_info_returns_complete_information(self):
        self.checker.filter_allowed_templates = Mock(side_effect=lambda x: x)
        self.checker.get_id.return_value = u"1"
        self.checker.has_valid_id.return_value = True
        self.mapper.get_commonscat_list_from_links.return_value = [u"Weblink Category"]
        self.mapper.get_commonscat.return_value = u"Category:Cultural heritage ensembles in Saxony"
        self.article.get.return_value = u" Test text {{Denkmalliste Sachsen Tabellenzeile|ID=1}} more text"
        info = self.collector.get_information(self.article, u"1")
        self.assertTrue(info.has_usable_id)
        self.assertTrue(info.has_valid_id)
        self.assertFalse(info.has_duplicate_ids)
        self.assertFalse(info.has_image)
        self.assertEqual(info.meta["template_count"], 1)
        self.assertEqual(info.category, u"Category:Cultural heritage ensembles in Saxony")

    def test_get_info_returns_id_validity(self):
        self.checker.filter_allowed_templates = Mock(side_effect=lambda x: x)
        self.checker.get_id.return_value = "1"
        self.checker.has_valid_id.return_value = False
        self.mapper.get_commonscat_list_from_links.return_value = [u"Weblink Category"]
        self.mapper.get_commonscat.return_value = u"Category:Cultural heritage ensembles in Saxony"
        self.article.get.return_value = u" Test text {{Denkmalliste Sachsen Tabellenzeile|ID=1}} more text"
        info = self.collector.get_information(self.article, u"1")
        self.assertTrue(info.has_usable_id)
        self.assertFalse(info.has_valid_id)

    def test_get_info_returns_duplicate_id_info(self):
        self.checker.filter_allowed_templates = Mock(side_effect=lambda x: x)
        self.checker.get_id.return_value = "1"
        self.checker.has_valid_id.return_value = True
        self.mapper.get_commonscat_list_from_links.return_value = [u"Weblink Category"]
        self.mapper.get_commonscat.return_value = u"Category:Cultural heritage ensembles in Saxony"
        self.article.get.return_value = u" Test text {{Denkmalliste Sachsen Tabellenzeile|ID=1}} more text" * 3
        info = self.collector.get_information(self.article, u"1")
        self.assertFalse(info.has_usable_id)
        self.assertEqual(info.meta["template_count"], 3)
        self.assertTrue(info.has_duplicate_ids)

    def test_get_most_specific_category_returns_first_non_empty_value(self):
        self.mapper.get_commonscat_list_from_links.return_value = [
            "",
            u"Category:Cultural heritage ensembles in Bavaria"
        ]
        text = u"{{Denkmalliste Bayern Tabellenzeile|ID=1}}"
        category = self.collector.get_most_specific_category(text)
        self.assertEqual(category, u"Category:Cultural heritage ensembles in Bavaria")

    def test_get_info_recognizes_existing_images(self):
        self.checker.filter_allowed_templates = Mock(side_effect=lambda x: x)
        self.checker.get_id.return_value = "1"
        self.checker.has_valid_id.return_value = True
        self.mapper.get_commonscat_list_from_links.return_value = [u"Weblink Category"]
        self.mapper.get_commonscat.return_value = u"Category:Cultural heritage ensembles in Saxony"
        self.article.get.return_value = u"{{Denkmalliste Sachsen Tabellenzeile|ID=1|Bild=Denkmal.jpg}}"
        info = self.collector.get_information(self.article, u"1")
        self.assertTrue(info.has_image)


if __name__ == '__main__':
    unittest.main()
