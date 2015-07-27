# -*- coding: utf-8 -*-
import unittest

from mock import Mock  # unittest.mock for Python >= 3.3

from wlmbots.lib import pagelist


class TestArticleIterator(unittest.TestCase):


    def test_article_iterator_iterates_over_categories(self):
        category_callback = Mock()
        it = pagelist.ArticleIterator(category_callback = category_callback)
        category = Mock()
        category.articles.return_value = []
        it.categories = [category]
        it.iterate_categories()
        category_callback.assert_called_once_with(category, 0, it)

    def test_article_iterator_iterates_over_articles(self):
        article_callback = Mock()
        it = pagelist.ArticleIterator(article_callback = article_callback)
        article1 = Mock()
        article2 = Mock()
        category = Mock()
        category.articles.return_value = [article1, article2]
        it.categories = [category]
        it.iterate_categories()
        article_callback.assert_any_call(article1, category, 0, it)
        article_callback.assert_any_call(article2, category, 1, it)


class TestArticleIteratorParamParser(unittest.TestCase):


    def test_limit_is_set(self):
        article_iterator = Mock()
        parser = pagelist.ArticleIteratorArgumentParser(article_iterator)
        parser.check_argument("-limit:5")
        self.assertEqual(article_iterator.limit, 5)


    def test_category_sets_pywikibot_category(self):
        raise NotImplementedError()
        # TODO

        
    def test_missing_category_sets_pywikibot_pagelist_all(self):
        raise NotImplementedError()
        # TODO


if __name__ == '__main__':
    unittest.main()
