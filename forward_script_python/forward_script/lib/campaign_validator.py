# -*- coding: utf-8 -*-
class CampaignValidator(object):

    CAMPAIGN_NAMESPACE = 460

    def __init__(self, pywikibot, site):
        self.pywikibot = pywikibot
        self.site = site

    def is_valid_campaign(self, campaign_name):
        page = self.pywikibot.Page(self.site, campaign_name, self.CAMPAIGN_NAMESPACE)
        return self._page_is_valid(page)

    @staticmethod
    def _page_is_valid(page):
        return page.exists() and not page.isRedirectPage()
