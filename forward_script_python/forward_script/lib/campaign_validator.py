class CampaignValidator(object):

    CAMPAIGN_NAMESPACE = 460

    def __init__(self, pywikibot):
        self.pywikibot = pywikibot

    def is_valid_campaign(self, campaign_name):
        page = self.pywikibot.Page(campaign_name)
        return self._page_is_valid(page) and self._page_is_campaign(page)

    @staticmethod
    def _page_is_valid(page):
        e = page.exists()
        r = page.isRedirectPage()
        return e and not r #page.exists() and not page.isRedirectPage()

    def _page_is_campaign(self, page):
        iscpn = page.namespace() == self.CAMPAIGN_NAMESPACE
        return iscpn
