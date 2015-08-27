#!/usr/bin/python
# -*- coding: utf-8  -*-
""" This script generates JSON information about monument data templates in wiki text. """

import argparse
import sys
import json
import codecs
import mwparserfromhell

from wlmbots.lib.template_checker import TemplateChecker
from wlmbots.lib.commonscat_mapper import CommonscatMapper


def get_template_info(template_checker, commonscat_mapper, text, monument_id=''):
    if not monument_id:
        return {
            "id_not_found": True,
            "category": get_most_specific_category(commonscat_mapper, text),
            "missing_monument_id": True
        }
    id_count = 0
    info = {}
    templates = mwparserfromhell.parse(text).filter_templates()
    for template in template_checker.filter_allowed_templates(templates):
        if template_checker.get_id(template) != monument_id:
            continue
        if id_count:
            id_count += 1
            continue
        id_count = 1
        info = {
            "template": unicode(template),
            "category": get_most_specific_category(commonscat_mapper, text, template),
            "valid_id": template_checker.has_valid_id(template),
            "image_exists": image_exists(template)
        }
    if info:
        info["duplicate_ids"] = id_count > 1
    else:
        info["id_not_found"] = True
        info["category"] = get_most_specific_category(commonscat_mapper, text)
    return info


def get_most_specific_category(commonscat_mapper, text, template=None):
    try:
        if template:
            return commonscat_mapper.get_commonscat(text, template)
        else:
            # return first non-empty element or fail
            return next(category for category in commonscat_mapper.get_commonscat_list_from_links(text) if category)
    except StopIteration:
        return ""


def image_exists(template):
    try:
        return template.get("Bild").value.strip() != ""
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser(description='Generate JSON info about monument data in wiki text.')
    parser.add_argument('--monument_id', '-i', help='Unique ID of the monument. Validity will be checked.',
                        default='', metavar='ID')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    args = parser.parse_args()
    checker = TemplateChecker()
    checker.load_config("config/templates.json")
    mapper = CommonscatMapper()
    info = get_template_info(checker, mapper, args.infile.read(), args.monument_id)
    utf8_writer = codecs.getwriter('utf8')
    json.dump(info, utf8_writer(sys.stdout))


if __name__ == "__main__":
    main()
