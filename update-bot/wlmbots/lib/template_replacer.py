import re


class TemplateReplacer(object):
    """ Replaces parameter values in a mwparserfromhell.Template node while
        preserving its whitespace.
    """

    def __init__(self, template):
        self.template = template

    def get_value(self, name):
        return self.template.get(name).value

    def set_value(self, name, value):
        param = self.template.get(name)
        whitespace = re.match(r"(\s*)(.*?)(\s*)$", unicode(param.value), re.UNICODE)
        if not whitespace:
            param.value = unicode(value)
        elif whitespace.group(2) == "" and whitespace.group(3) == "":
            line_end = re.search("(.*?)(\r?\n)$", whitespace.group(1))
            if line_end:
                param.value = line_end.group(1) + unicode(value) + line_end.group(2)
            else:
                param.value = whitespace.group(1) + unicode(value)
        else:
            param.value = whitespace.group(1) + unicode(value) + whitespace.group(3)

    def get_available_params(self):
        return [p.name.strip() for p in self.template.params]

    def param_is_empty(self, name):
        try:
            return self.get_value(name).strip() == ""
        except ValueError:
            return True

    def __unicode__(self):
        return unicode(self.template)

    def __str__(self):
        return unicode(self).encode('utf-8')
