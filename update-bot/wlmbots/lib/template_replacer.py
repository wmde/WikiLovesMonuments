import re


class TemplateReplacer(object):
    """ Replaces parameter values in a mwparserfromhell.Template node while
        preserving its whitespace.
    """

    def __init__(self, template):
        self.template = template
        self.params_dict = {}
        # ordered list of parameter names (with and without whitespace) to preserve the original order of params in the template
        self.params_index = []
        self.params_parsed = False
        self._parse_params()

    def get_value(self, name):
        return self.params_dict[name].value

    def set_value(self, name, value):
        whitespace = re.match(r"(\s*)(.*?)(\s*)$", unicode(self.params_dict[name].value), re.UNICODE)
        if not whitespace:
            self.params_dict[name].value = unicode(value)
        elif whitespace.group(2) == "" and whitespace.group(3) == "":
            line_end = re.search("(.*?)(\r?\n)$", whitespace.group(1))
            if line_end:
                self.params_dict[name].value = line_end.group(1) + unicode(value) + line_end.group(2)
            else:
                self.params_dict[name].value = whitespace.group(1) + unicode(value)
        else:
            self.params_dict[name].value = whitespace.group(1) + unicode(value) + whitespace.group(3)

    def get_available_params(self):
        return [p["name_key"] for p in self.params_index]

    def param_is_empty(self, name):
        try:
            return self.params_dict[name].value.strip() == ""
        except KeyError:
            return True

    def __unicode__(self):
        template = u"{{" + unicode(self.template.name)
        for param in self.params_index:
            template += u"|" + unicode(self.params_dict[param["name_key"]])
        template += u"}}"
        return template

    def __str__(self):
        return unicode(self).encode('utf-8')

    def _parse_params(self):
        if self.params_parsed:
            return
        self.params_index = [None] * len(self.template.params)
        for idx, parameter in enumerate(self.template.params):
            name = parameter.name
            name_key = name.strip()
            self.params_dict[name_key] = parameter
            self.params_index[idx] = {"name": name, "name_key": name_key}
        self.params_parsed = True
