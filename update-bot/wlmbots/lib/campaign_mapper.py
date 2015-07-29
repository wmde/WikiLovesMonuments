"""
The class CampaignMapper uses a CommonscatMapper to map page list catgeories to campaign names
"""

import json


class CampaignMapper(object):

    def __init__(self, commonscat_mapper):
        self.commonscat_mapper = commonscat_mapper
        self.mapping = {}


    def load_mapping(self, filename):
        with open(filename, "r") as mapconf:
            self.mapping = json.load(mapconf)


    def get_campaign(self, category):
        return self.mapping[self.commonscat_mapper.mapping[category]]
