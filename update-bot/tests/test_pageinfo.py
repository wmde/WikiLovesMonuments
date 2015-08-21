# -*- coding: utf-8 -*-
import unittest

from mock import Mock  # unittest.mock for Python >= 3.3

from wlmbots import pageinfo


class TestPageinfo(unittest.TestCase):

    def setUp(self):
        self.mapper = Mock()
        self.checker = Mock()

    def test_get_info_returns_not_found_if_id_does_not_match(self):
        self.checker.is_allowed_template.return_value = True
        self.checker.get_id.return_value = "1"
        self.mapper.get_commonscat_from_weblinks_template.return_value = "Weblink Category"
        text = "{{Denkmalliste Sachsen Tabellenzeile|ID=1}}"
        info = pageinfo.get_template_info(self.checker, self.mapper, text, "123")
        self.assertEqual(info, {"id_not_found": True, "category": "Weblink Category"})

    def test_get_info_returns_not_found_if_template_is_not_configured(self):
        self.checker.is_allowed_template.return_value = False
        self.mapper.get_commonscat_from_weblinks_template.return_value = "Weblink Category"
        text = "{{Denkmalliste Sachsen Tabellenzeile|ID=1}}"
        info = pageinfo.get_template_info(self.checker, self.mapper, text, "123")
        self.assertEqual(info, {"id_not_found": True, "category": "Weblink Category"})

    def test_get_info_accepts_empty_id(self):
        self.checker.is_allowed_template.return_value = False
        self.mapper.get_commonscat_from_weblinks_template.return_value = "Weblink Category"
        text = "{{Denkmalliste Sachsen Tabellenzeile|ID=1}}"
        info = pageinfo.get_template_info(self.checker, self.mapper, text, "")
        self.assertEqual(info, {"id_not_found": True, "category": "Weblink Category"})

    def test_get_info_returns_info(self):
        self.checker.is_allowed_template.return_value = True
        self.checker.get_id.return_value = "1"
        self.checker.has_valid_id.return_value = True
        self.mapper.get_commonscat_from_table_row_template.return_value = u"Category:Cultural heritage ensembles in Saxony"
        text = u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}"
        info = pageinfo.get_template_info(self.checker, self.mapper, text, "1")
        self.assertEqual(info, {
            "template": u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}",
            "category": u"Category:Cultural heritage ensembles in Saxony",
            "valid_id": True,
            "duplicate_ids": False
        })

    def test_get_info_returns_id_validity(self):
        self.checker.is_allowed_template.return_value = True
        self.checker.get_id.return_value = "1"
        self.checker.has_valid_id.return_value = False
        self.mapper.get_commonscat_from_table_row_template.return_value = u"Category:Cultural heritage ensembles in Saxony"
        text = u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}"
        info = pageinfo.get_template_info(self.checker, self.mapper, text, "1")
        self.assertEqual(info, {
            "template": u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}",
            "category": u"Category:Cultural heritage ensembles in Saxony",
            "valid_id": False,
            "duplicate_ids": False
        })

    def test_get_info_returns_duplicate_id_info(self):
        self.checker.is_allowed_template.return_value = True
        self.checker.get_id.return_value = "1"
        self.checker.has_valid_id.return_value = True
        self.mapper.get_commonscat_from_table_row_template.return_value = u"Category:Cultural heritage ensembles in Saxony"
        text = u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}{{Denkmalliste Sachsen Tabellenzeile|ID=1}}"
        info = pageinfo.get_template_info(self.checker, self.mapper, text, "1")
        self.assertEqual(info, {
            "template": u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}",
            "category": u"Category:Cultural heritage ensembles in Saxony",
            "valid_id": True,
            "duplicate_ids": True
        })

    def test_get_info_has_different_sources_for_category_info(self):
        self.checker.is_allowed_template.return_value = True
        self.checker.get_id.return_value = "1"
        self.checker.has_valid_id.return_value = True
        self.mapper.get_commonscat_from_table_row_template.return_value = ""
        self.mapper.get_commonscat_from_weblinks_template.return_value = u"Category:Cultural heritage ensembles in Bavaria"
        text = u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}"
        info = pageinfo.get_template_info(self.checker, self.mapper, text, "1")
        self.assertEqual(info, {
            "template": u"{{Denkmalliste Sachsen Tabellenzeile|ID=1}}",
            "category": u"Category:Cultural heritage ensembles in Bavaria",
            "valid_id": True,
            "duplicate_ids": False
        })
