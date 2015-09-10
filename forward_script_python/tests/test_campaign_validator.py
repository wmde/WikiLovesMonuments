# -*- coding: utf-8 -*-
import unittest

from mock import Mock

from forward_script.lib.campaign_validator import CampaignValidator


class TestCampaignChecker(unittest.TestCase):

    def setUp(self):
        self.pywikibot = Mock()
        self.checker = CampaignValidator(self.pywikibot, site=Mock())

    def test_page_must_exist_to_be_valid(self):
        page = Mock()
        page.exists.return_value = False
        self.pywikibot.Page.return_value = page
        self.assertEqual(self.checker.is_valid_campaign("Test Campaign"), False)
        page.exists.return_value = True
        page.isRedirectPage.return_value = True
        self.pywikibot.Page.return_value = page
        self.assertEqual(self.checker.is_valid_campaign("Test Campaign"), False)

    def test_valid_campaign_page(self):
        page = Mock()
        page.exists.return_value = True
        page.isRedirectPage.return_value = False
        self.pywikibot.Page.return_value = page
        self.assertTrue(self.checker.is_valid_campaign("Test Campaign"))


if __name__ == '__main__':
    unittest.main()
