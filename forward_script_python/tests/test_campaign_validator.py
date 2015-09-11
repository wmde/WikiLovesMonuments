# -*- coding: utf-8 -*-
import unittest

from mock import Mock

from forward_script.lib.campaign_validator import CampaignValidator


class TestCampaignChecker(unittest.TestCase):

    def setUp(self):
        self.site = Mock()
        self.checker = CampaignValidator(self.site)

    def test_page_must_exist_to_be_valid(self):
        page = Mock()
        page.exists = False
        self.site.Pages = {"Campaign:Test Campaign": page}
        self.assertEqual(self.checker.is_valid_campaign("Test Campaign"), False)
        page.exists = True
        page.redirect = True
        self.assertEqual(self.checker.is_valid_campaign("Test Campaign"), False)
        page.exists = True
        page.redirect = False
        page.namespace = 0
        self.assertEqual(self.checker.is_valid_campaign("Test Campaign"), False)


    def test_valid_campaign_page(self):
        page = Mock()
        page.exists = True
        page.redirect = False
        page.namespace = CampaignValidator.CAMPAIGN_NAMESPACE
        self.site.Pages = {"Campaign:Test Campaign": page}
        self.assertTrue(self.checker.is_valid_campaign("Test Campaign"))


if __name__ == '__main__':
    unittest.main()
