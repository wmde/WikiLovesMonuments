import mwparserfromhell


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

    def __init__(self, template_checker, commonscat_mapper):
        """

        :param template_checker:
        :type template_checker: wlmbots.lib.template_checker.TemplateChecker
        :param commonscat_mapper: wlmbots.lib.commonscat_mapper.CommonscatMapper
        :return:
        """
        self.template_checker = template_checker
        self.commonscat_mapper = commonscat_mapper

    def get_information(self, article, monument_id):
        info = PageInformation()
        text = article.get()
        info.category = self.get_most_specific_category(text)
        if not monument_id:
            return info
        id_count = 0
        templates = mwparserfromhell.parse(text).filter_templates()
        for template in self.template_checker.filter_allowed_templates(templates):
            if self.template_checker.get_id(template) != monument_id:
                continue
            if id_count:
                id_count += 1
                continue
            id_count = 1
            info.category = self.get_most_specific_category(text, template)
            info.id = monument_id
            info.has_valid_id = self.template_checker.has_valid_id(template)
        if info.id:
            info.has_duplicate_ids = id_count > 1
        return info

    def get_most_specific_category(self, text, template=None):
        try:
            if template:
                return self.commonscat_mapper.get_commonscat(text, template)
            else:
                commonscat_list = self.commonscat_mapper.get_commonscat_list_from_links(text)
                # return first non-empty element or fail
                return next(category for category in commonscat_list if category)
        except StopIteration:
            return ""

    @staticmethod
    def image_exists(template):
        try:
            return template.get("Bild").value.strip() != ""
        except ValueError:
            return False
