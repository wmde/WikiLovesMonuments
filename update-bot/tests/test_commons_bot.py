# -*- coding: utf-8 -*-
import unittest
import pywikibot
from mock import Mock  # unittest.mock for Python >= 3.3

from wlmbots import commons_bot


class TestCommonsBotFunctions(unittest.TestCase):

    def test_default_start_time_returns_1st_of_month(self):
        date = Mock()
        date.year = 2015
        date.month = 9
        date.day = 25
        default_start_time = commons_bot.default_start_time(date)
        self.assertEqual(default_start_time.year, 2015)
        self.assertEqual(default_start_time.month, 9)
        self.assertEqual(default_start_time.day, 1)

class TestCommonsBot(unittest.TestCase):

    def setUp(self):
        self.commons_site = Mock()
        self.wikipedia_site = Mock()
        self.article_iterator = Mock()
        self.commons_bot = commons_bot.CommonsBot(self.commons_site, self.wikipedia_site, self.article_iterator)

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
        pywikibot.error = Mock()
        self.commons_bot.cb_check_article(article)
        self.commons_bot.insert_image.assert_not_called()
        pywikibot.error.assert_called_once()

    def test_check_article_calls_insert_image_with_params(self):
        article = Mock()
        article.title.return_value = u"File:Test Image.jpg"
        article.get.return_value = u"Test text <-- LIST_CALLBACK_PARAMS de|Test Page|123 -->\n\n"
        self.commons_bot.insert_image = Mock()
        self.commons_bot.cb_check_article(article)
        self.commons_bot.insert_image.assert_called_once_with(u"File:Test Image.jpg", u"Test Page", "123")

if __name__ == '__main__':
    unittest.main()
