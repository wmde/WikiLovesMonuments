# -*- coding: utf-8 -*-
import unittest
from mock import Mock  # unittest.mock for Python >= 3.3

from wlmbots import commons_bot
from wlmbots.lib.template_checker import TemplateChecker
import collections


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
        self.commons_bot.cb_check_article(article)
        self.assertEqual(self.commons_bot.images, {})

    def test_check_article_does_nothing_if_params_comment_has_wrong_format(self):
        article = Mock()
        article.get.return_value = u"Test text <!-- WIKIPAGE_UPDATE_PARAMS de|Test Page -->\n\n"
        self.commons_bot.cb_check_article(article)
        self.assertEqual(self.commons_bot.images, {})
        self.commons_bot.logger.error.assert_called_once()

    def test_check_article_appends_image_data(self):
        article = Mock()
        article.title.return_value = u"File:Test Image.jpg"
        article.get.return_value = u"Test text <!-- WIKIPAGE_UPDATE_PARAMS de|Test Page|123 -->\n\n"
        self.commons_bot.cb_check_article(article)
        expected_image_data = collections.defaultdict(list)
        expected_image_data[u"Test Page"] = [{
            "commons_article": article,
            "monument_id": u"123",
            "update_params_comment": u"<!-- WIKIPAGE_UPDATE_PARAMS de|Test Page|123 -->\n\n"
        }]
        self.assertEqual(self.commons_bot.images, expected_image_data)

    def test_insert_accumulated_edits_calls_image_inserter(self):
        article = Mock()
        article.title.return_value = u"File:Test Image.jpg"
        article.get.return_value = u"Test text <!-- WIKIPAGE_UPDATE_PARAMS de|Test Page|123 -->\n\n"
        wikipedia_article = Mock()
        test_page_edits = [
            {
                "commons_article": article,
                "monument_id": u"123",
                "update_params_comment": u"<!-- WIKIPAGE_UPDATE_PARAMS de|Test Page|123 -->\n\n"
            }
        ]
        self.commons_bot.fetch_page = Mock(return_value=wikipedia_article)
        self.commons_bot.images = {
            "Test Page": test_page_edits
        }
        self.commons_bot.insert_accumulated_edits()
        self.commons_bot.fetch_page.assert_called_once_with(u"Test Page")
        self.article_inserter.insert_images.assert_called_once_with(wikipedia_article, test_page_edits)

    def test_check_article_removes_comment_from_commons(self):
        article = Mock()
        article.title.return_value = u"File:Test Image.jpg"
        article.get.return_value = u"Test text <!-- WIKIPAGE_UPDATE_PARAMS de|Test Page|123 -->\n\n"
        self.commons_bot.fetch_page = Mock()
        self.commons_bot.images = {
            "Test Page": [
                {
                    "commons_article": article,
                    "monument_id": u"123",
                    "update_params_comment": u"<!-- WIKIPAGE_UPDATE_PARAMS de|Test Page|123 -->\n\n"
                }
            ]
        }
        self.commons_bot.insert_accumulated_edits()
        self.article_inserter.insert_images.return_value = True
        self.assertEquals(article.text, u"Test text ")
        article.save.assert_called_once()


class TestImageInserter(unittest.TestCase):

    def setUp(self):
        self.template_checker = TemplateChecker({
            u"Denkmalliste Bayern Tabellenzeile": {
                "id": u"Nummer",
                "id_check": r".+"
            }
        })
        self.logger = Mock()
        self.inserter = commons_bot.ImageInserter(self.template_checker, self.logger)

    def test_insert_images_checks_if_article_exists(self):
        article = Mock()
        article.title.return_value = u"Missing article"
        article.exists.return_value = False
        with self.assertRaises(commons_bot.CommonsBotException):
            self.inserter.insert_images(article, [])

    def test_insert_images_inserts_image_name_without_prefix(self):
        article = Mock()
        article.exists.return_value = True
        article.get.return_value = u"{{Denkmalliste Bayern Tabellenzeile|Bild=|Nummer=123}}"
        commons_article = Mock()
        commons_article.title.return_value = u"File:Test Image.jpg"
        edits = [
            {"commons_article": commons_article, "monument_id": u"123"}
        ]
        self.assertTrue(self.inserter.insert_images(article, edits))
        self.assertEqual(article.text, u"{{Denkmalliste Bayern Tabellenzeile|Bild=Test Image.jpg|Nummer=123}}")

    def test_insert_images_can_insert_multiple_images(self):
        article = Mock()
        article.exists.return_value = True
        article.get.return_value = u"{{Denkmalliste Bayern Tabellenzeile|Bild=|Nummer=123}}\n" + \
                                   u"{{Denkmalliste Bayern Tabellenzeile|Bild=|Nummer=124}}"
        commons_article1 = Mock()
        commons_article1.title.return_value = u"File:Test Image.jpg"
        commons_article2 = Mock()
        commons_article2.title.return_value = u"File:Another Test Image.jpg"
        edits = [
            {"commons_article": commons_article1, "monument_id": u"123"},
            {"commons_article": commons_article2, "monument_id": u"124"}
        ]
        self.assertTrue(self.inserter.insert_images(article, edits))
        self.assertEqual(article.text,
                         u"{{Denkmalliste Bayern Tabellenzeile|Bild=Test Image.jpg|Nummer=123}}\n" +
                         u"{{Denkmalliste Bayern Tabellenzeile|Bild=Another Test Image.jpg|Nummer=124}}")

    def test_insert_images_skips_image_if_image_is_not_empty(self):
        article = Mock()
        article.exists.return_value = True
        article.get.return_value = u"{{Denkmalliste Bayern Tabellenzeile|Bild=File:Test Image 2.jpg|Nummer=123}}"
        commons_article = Mock()
        edits = [
            {"commons_article": commons_article, "monument_id": u"123"}
        ]
        self.assertFalse(self.inserter.insert_images(article, edits))
        self.logger.log.assert_called_once()

    def test_insert_images_logs_error_if_not_all_images_can_be_inserted(self):
        article = Mock()
        article.exists.return_value = True
        article.get.return_value = u"{{Denkmalliste Bayern Tabellenzeile|Bild=|Nummer=123}}"
        commons_article1 = Mock()
        commons_article1.title.return_value = u"File:Test Image.jpg"
        commons_article2 = Mock()
        commons_article2.title.return_value = u"File:Another Test Image.jpg"
        edits = [
            {"commons_article": commons_article1, "monument_id": u"123"},
            {"commons_article": commons_article2, "monument_id": u"124"}
        ]
        self.assertTrue(self.inserter.insert_images(article, edits))
        expected_error = "1 image(s) could not be inserted, probably because of removed table rows"
        self.logger.error.assert_called_once_with(expected_error)


if __name__ == '__main__':
    unittest.main()
