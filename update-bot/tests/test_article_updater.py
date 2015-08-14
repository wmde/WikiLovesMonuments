# -*- coding: utf-8 -*-
import unittest

from mock import Mock

from wlmbots.lib.article_updater import ArticleUpdater


class TestArticleUpdater(unittest.TestCase):

    def setUp(self):
        self.article = Mock()

    def test_text_is_inserted_if_article_does_not_exist(self):
        updater = ArticleUpdater(self.article)
        self.article.exists.return_value = False
        self.assertTrue(updater.save_text("Test"))
        self.assertEqual(self.article.text, "Test")
        self.article.save.assert_called_once()

    def test_article_is_saved_if_text_is_different(self):
        updater = ArticleUpdater(self.article)
        self.article.exists.return_value = True
        self.article.get.return_value = "Old Test"
        self.assertTrue(updater.save_text("New Test"))
        self.assertEqual(self.article.text, "New Test")
        self.article.save.assert_called_once()

    def test_article_is_not_saved_if_text_is_not_changed(self):
        updater = ArticleUpdater(self.article)
        self.article.exists.return_value = True
        self.article.get.return_value = "Test"
        self.assertFalse(updater.save_text("Test"))
        self.assertEqual(self.article.save.call_count, 0)

    def test_text_between_markers_is_changed(self):
        updater = ArticleUpdater(self.article, "B", "E")
        self.article.exists.return_value = True
        self.article.get.return_value = "Foo<!--B-->Old\nTest<!--E-->Bar"
        self.assertTrue(updater.save_text("New Test"))
        self.assertEqual(self.article.text, "Foo<!--B-->New Test<!--E-->Bar")
        self.article.save.assert_called_once()

    def test_text_between_markers_is_not_changed_if_text_is_the_same(self):
        updater = ArticleUpdater(self.article, "B", "E")
        self.article.exists.return_value = True
        self.article.get.return_value = "Foo<!--B-->Test<!--E-->Bar"
        self.assertFalse(updater.save_text("Test"))
        self.assertEqual(self.article.save.call_count, 0)

    def test_whitespace_after_start_marker_is_preserved(self):
        updater = ArticleUpdater(self.article, "B", "E")
        self.article.exists.return_value = True
        self.article.get.return_value = "Foo<!--B-->\nOld Test <!--E-->Bar"
        self.assertTrue(updater.save_text("New Test"))
        self.assertEqual(self.article.text, "Foo<!--B-->\nNew Test<!--E-->Bar")
        self.article.save.assert_called_once()
