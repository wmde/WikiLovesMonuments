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
        self.article_inserter = Mock()
        self.commons_bot = commons_bot.CommonsBot(self.wikipedia_site, self.article_inserter)
        self.commons_bot.logger = Mock()
        self.commons_article = Mock()
        self.commons_article.title.return_value = u"File:Test Image.jpg"
        self.commons_article.userName.return_value = u"Test User"

    def test_check_article_does_nothing_if_params_comment_is_missing(self):
        article = Mock()
        article.get.return_value = "Test text"
        self.commons_bot.insert_image = Mock()
        self.commons_bot.cb_check_article(article)
        self.commons_bot.insert_image.assert_not_called()

    def test_check_article_does_nothing_if_params_comment_has_wrong_format(self):
        article = Mock()
        article.get.return_value = u"Test text <!-- WIKIPAGE_UPDATE_PARAMS de|Test Page -->\n\n"
        self.commons_bot.insert_image = Mock()
        self.commons_bot.cb_check_article(article)
        self.commons_bot.insert_image.assert_not_called()
        self.commons_bot.logger.error.assert_called_once()

    def test_check_article_calls_article_inserter(self):
        article = Mock()
        article.title.return_value = u"File:Test Image.jpg"
        article.get.return_value = u"Test text <!-- WIKIPAGE_UPDATE_PARAMS de|Test Page|123 -->\n\n"
        wiki_article = Mock()
        self.commons_bot.fetch_page = Mock(return_value=wiki_article)
        self.commons_bot.cb_check_article(article)
        self.article_inserter.insert_images.assert_called_once_with(wiki_article, [
            {"commons_article": article, "monument_id": u"123"}
        ])

    def test_check_article_removes_comment_from_commons(self):
        article = Mock()
        article.title.return_value = u"File:Test Image.jpg"
        article.get.return_value = u"Test text <!-- WIKIPAGE_UPDATE_PARAMS de|Test Page|123 -->\n\n"
        self.commons_bot.fetch_page = Mock()
        self.commons_bot.cb_check_article(article)
        self.article_inserter.insert_images.return_value = True
        self.assertEquals(article.text, u"Test text ")
        article.save.assert_called_once()


class TestImageInserter(unittest.TestCase):

    def setUp(self):
        self.template_checker = Mock()
        self.logger = Mock()
        self.inserter = commons_bot.ImageInserter(self.template_checker, self.logger)

    def test_insert_images_inserts_image_name_without_prefix(self):
        article = Mock()
        article.exists.return_value = True
        article.get.return_value = u"{{Denkmalliste Bayern Tabellenzeile|Bild=|Nummer=123}}"
        self.template_checker.get_id.return_value = u"123"
        self.template_checker.get_id_name.return_value = u"Nummer"
        commons_article = Mock()
        commons_article.title.return_value = u"File:Test Image.jpg"
        edits = [
            {"commons_article": commons_article, "monument_id": u"123"}
        ]
        self.assertTrue(self.inserter.insert_images(article, edits))
        self.assertEqual(article.text, u"{{Denkmalliste Bayern Tabellenzeile|Bild=Test Image.jpg|Nummer=123}}")

    def test_insert_images_skips_image_if_image_is_not_empty(self):
        article = Mock()
        article.exists.return_value = True
        article.get.return_value = u"{{Denkmalliste Bayern Tabellenzeile|Bild=File:Test Image 2.jpg|Nummer=123}}"
        self.template_checker.get_id.return_value = u"123"
        self.template_checker.get_id_name.return_value = u"Nummer"
        commons_article = Mock()
        edits = [
            {"commons_article": commons_article, "monument_id": u"123"}
        ]
        self.assertFalse(self.inserter.insert_images(article, edits))
        self.logger.log.assert_called_once()


if __name__ == '__main__':
    unittest.main()
