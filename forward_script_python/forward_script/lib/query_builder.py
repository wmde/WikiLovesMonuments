# -*- coding: utf-8 -*-
import urllib


class QueryBuilder(object):

    def get_query(self, info, page_name, object_id='', coordinates=None, additional_categories=None):
        """
        Generate a query string from available information
        @type info: PageInformation
        @type page_name: String
        @type object_id: String
        @type coordinates: dict
        @type additional_categories: list
        @return string url encoded querystring
        """

        if coordinates is None:
            coordinates = {}
        if additional_categories is None:
            additional_categories = []

        query = {}
        categories = '|' . join([info.get_category()] + additional_categories)
        query['categories'] = categories
        if 'lat' in coordinates and coordinates['lat'] and 'lon' in coordinates and coordinates['lon']:
            query['lat'] = coordinates['lat']
            query['lon'] = coordinates['lon']
        if info.has_usable_id():
            query['objref'] = '|' . join(['de', page_name, object_id])
        if info.has_valid_id():
            query['fields[]'] = object_id
        if not info.has_image():
            query['updateList'] = "1"
        return "&" + urllib.urlencode(query)
