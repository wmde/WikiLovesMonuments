# -*- coding: utf-8 -*-
import unittest
from mock import Mock  # unittest.mock for Python >= 3.3

from wlmbots import commons_bot


class TestCommonsBotFunctions(unittest.TestCase):

    def test_first_day_of_month_sets_correct_day(self):
        date = Mock()
        date.year = 2015
        date.month = 9
        date.day = 25
        first_day_of_month = commons_bot.first_day_of_month(date)
        self.assertEqual(first_day_of_month.year, 2015)
        self.assertEqual(first_day_of_month.month, 9)
        self.assertEqual(first_day_of_month.day, 1)

class TestCommonsBot(unittest.TestCase):

    def setUp(self):
        self.wikipedia_site = Mock()
        self.article_iterator = Mock()
        self.template_checker = Mock()
        self.commons_bot = commons_bot.CommonsBot(self.wikipedia_site, self.article_iterator, self.template_checker)
        self.commons_bot.logger = Mock()

    def test_check_article_does_nothing_if_params_comment_is_missing(self):
        article = Mock()
        article.get.return_value = "Test text"
        self.commons_bot.insert_image = Mock()
        self.commons_bot.cb_check_article(article)
        self.commons_bot.insert_image.assert_not_called()

    def test_check_article_does_nothing_if_params_comment_has_wrong_format(self):
        article = Mock()
        article.get.return_value = u"Test text <-- LIST_CALLBACK_PARAMS de|Test Page -->\n\n"
        self.commons_bot.insert_image = Mock()
        self.commons_bot.cb_check_article(article)
        self.commons_bot.insert_image.assert_not_called()
        self.commons_bot.logger.error.assert_called_once()

    def test_check_article_calls_insert_image_with_params(self):
        article = Mock()
        article.title.return_value = u"File:Test Image.jpg"
        article.get.return_value = u"Test text <-- LIST_CALLBACK_PARAMS de|Test Page|123 -->\n\n"
        self.commons_bot.insert_image = Mock()
        self.commons_bot.cb_check_article(article)
        self.commons_bot.insert_image.assert_called_once_with(u"File:Test Image.jpg", u"Test Page", "123")

    def test_check_article_removes_comment_from_commons(self):
        article = Mock()
        article.title.return_value = u"File:Test Image.jpg"
        article.get.return_value = u"Test text <-- LIST_CALLBACK_PARAMS de|Test Page|123 -->\n\n"
        self.commons_bot.insert_image = Mock()
        self.commons_bot.cb_check_article(article)
        self.assertEquals(article.text, u"Test text ")
        article.save.assert_called_once()

    def test_insert_image_checks_pagename(self):
        page = Mock()
        page.exists.return_value = False
        self.commons_bot.fetch_page = Mock(return_value=page)
        with self.assertRaises(commons_bot.CommonsBotException):
            self.commons_bot.insert_image("File:Test Image.jpg", "", "123")

    def test_insert_image_checks_if_id_exists(self):
        page = Mock()
        page.exists.return_value = True
        page.get.return_value = "{{Denkmalliste Bayern Tabellenzeile|Bild=|Nummer=77}}"
        self.template_checker.get_id.return_value = "77"
        self.commons_bot.fetch_page = Mock(return_value=page)
        with self.assertRaises(commons_bot.CommonsBotException):
            self.commons_bot.insert_image("File:Test Image.jpg", "Test Page", "123")

    def test_insert_image_inserts_image_name_without_prefix_and_saves(self):
        page = Mock()
        page.exists.return_value = True
        page.get.return_value = "{{Denkmalliste Bayern Tabellenzeile|Bild=|Nummer=123}}"
        self.template_checker.get_id.return_value = "123"
        self.template_checker.get_id_name.return_value = "Nummer"
        self.commons_bot.fetch_page = Mock(return_value=page)
        self.assertTrue(self.commons_bot.insert_image("File:Test Image.jpg", "Test Page", "123"))
        self.assertEqual(page.text, "{{Denkmalliste Bayern Tabellenzeile|Bild=Test Image.jpg|Nummer=123}}")
        page.save.assert_called_once()

    def test_insert_image_skips_image_if_image_is_not_empty(self):
        page = Mock()
        page.exists.return_value = True
        page.get.return_value = "{{Denkmalliste Bayern Tabellenzeile|Bild=File:Test Image 2.jpg|Nummer=123}}"
        self.template_checker.get_id.return_value = "123"
        self.template_checker.get_id_name.return_value = "Nummer"
        self.commons_bot.fetch_page = Mock(return_value=page)
        self.assertFalse(self.commons_bot.insert_image("File:Test Image.jpg", "Test Page", "123"))
        page.save.assert_not_called()
        self.commons_bot.logger.log.assert_called_once()



if __name__ == '__main__':
    unittest.main()
