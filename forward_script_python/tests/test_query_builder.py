# -*- coding: utf-8 -*-
import unittest

from forward_script.lib.query_builder import QueryBuilder
from mock import Mock


class TestQueryBuilder(unittest.TestCase):

    def setUp(self):
        self._page_info = Mock()

    def test_category_is_added(self):
        qb = QueryBuilder()
        self._page_info.get_category.return_value = 'Test'
        query = qb.get_query(self._page_info, 'Test_Page')
        self.assertTrue('&categories=Test' in query)

    def test_additional_categories_are_added(self):
        qb = QueryBuilder()
        self._page_info.get_category.return_value = 'Test'
        query = qb.get_query(self._page_info, 'Test Page', '', None, ['Foo', 'Bar'])
        self.assertTrue('&categories=Test%7CFoo%7CBar' in query)

    def test_lat_and_lon_are_added(self):
        qb = QueryBuilder()
        self._page_info.get_category.return_value = ''
        query = qb.get_query(self._page_info, 'Test Page', '', {'lat': 1, 'lon': 2.2335455})
        self.assertTrue('&lat=1' in query)
        self.assertTrue('&lon=2.2335455' in query)

    def test_empty_lat_and_lon_are_filtered(self):
        qb = QueryBuilder()
        self._page_info.get_category.return_value = ''
        query = qb.get_query(self._page_info, 'Test Page', '', {'lat': '', 'lon': ''})
        self.assertFalse('&lat=' in query)
        self.assertFalse('&lon=' in query)

    def test_objref_is_added_if_id_is_usable(self):
        qb = QueryBuilder()
        self._page_info.get_category.return_value = ''
        self._page_info.has_usable_id.return_value = True
        query = qb.get_query(self._page_info, 'Test Page', '123')
        self.assertTrue('&objref=de%7CTest+Page%7C123' in query)

    def test_objref_is_left_out_if_id_is_not_usable(self):
        qb = QueryBuilder()
        self._page_info.get_category.return_value = ''
        self._page_info.has_usable_id.return_value = False
        query = qb.get_query(self._page_info, 'Test Page', '123')
        self.assertFalse('&objref=de%7CTest+Page%7C123' in query)

    def test_fields_are_added_if_id_is_valid(self):
        qb = QueryBuilder()
        self._page_info.get_category.return_value = ''
        self._page_info.has_valid_id.return_value = True
        query = qb.get_query(self._page_info, 'Test Page', '123')
        self.assertTrue('&fields%5B%5D=123' in query)

    def test_fields_are_left_out_if_id_is_invalid(self):
        qb = QueryBuilder()
        self._page_info.get_category.return_value = ''
        self._page_info.has_valid_id.return_value = False
        query = qb.get_query(self._page_info, 'Test Page', '123')
        self.assertFalse('&fields%5B%5D=123' in query)

    def test_update_list_is_added_if_no_image_exists(self):
        qb = QueryBuilder()
        self._page_info.get_category.return_value = ''
        self._page_info.has_image.return_value = False
        query = qb.get_query(self._page_info, 'Test Page', '123')
        self.assertTrue('&updateList=1' in query)

    def test_update_list_is_left_out_if_image_exists(self):
        qb = QueryBuilder()
        self._page_info.get_category.return_value = ''
        self._page_info.has_image.return_value = True
        query = qb.get_query(self._page_info, 'Test Page', '123')
        self.assertFalse('&updateList=1' in query)

if __name__ == '__main__':
    unittest.main()
