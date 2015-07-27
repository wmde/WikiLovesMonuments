class TableReplacer(object):
    """ This class represents a single table row on a wiki page """

    def __init__(self, text, row_dict):
        """ @param text Full page text
            @param row_dict Dictionary of row_name => column_index
        """
        self.text = text
        self.row_dict = row_dict
        self.columns = [""] * len(row_dict)
        # TODO parse columns, preserving the original formatting (linebreaks, styling, etc)

    def get_value(self, name):
        return self.columns[row_dict[name]]

    def set_value(self, name, value):
        # TODO Replace column value, preserving line breaks and formatting instructions
        pass

    def param_is_empty(self, name):
        return self.get_value(name).strip() == ""

    def __unicode__(self):
        # TODO string column values back together
        return u""
