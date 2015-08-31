class PageInformation(object):
    """
    Holds information about a page concerning the ID and image found in the page templates.
    """

    def __init__(self):
        self.category = u""
        self.id = u""
        self.has_duplicate_ids = False
        self.id_was_found = False
        self.has_image = False
        self.has_valid_id = False

    @property
    def has_usable_id(self):
        return self.id and not self.has_duplicate_ids


class PageInformationCollector(object):

    def __init__(self, pywikibot):
        self.pywikibot = pywikibot

    def get_information(self, page_title, monument_id):
        # TODO Implement this
        raise NotImplementedError
