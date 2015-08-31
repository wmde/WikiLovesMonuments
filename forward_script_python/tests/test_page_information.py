# -*- coding: utf-8 -*-
import unittest

from forward_script.lib.page_information import PageInformation


class TestPageInformation(unittest.TestCase):

    def test_has_usable_id(self):
        page_information = PageInformation()
        self.assertFalse(page_information.has_usable_id)
        page_information.id = "123"
        self.assertTrue(page_information.has_usable_id)
        page_information.has_duplicate_ids = True
        self.assertFalse(page_information.has_usable_id)


if __name__ == '__main__':
    unittest.main()
