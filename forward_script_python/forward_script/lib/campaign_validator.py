# -*- coding: utf-8 -*-
class CampaignValidator(object):

    CAMPAIGN_NAMESPACE = 460

    def __init__(self, site):
        self.site = site

    def is_valid_campaign(self, campaign_name):
        page = self.site.Pages["Campaign:" + campaign_name]
        return self._page_is_valid(page)

    def _page_is_valid(self, page):
        return page.exists and not page.redirect and page.namespace == self.CAMPAIGN_NAMESPACE
