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

def get_template_info(template_checker, commonscat_mapper, text, monument_id):
    id_count = 0
    info = {}
    for template in mwparserfromhell.parse(text).filter_templates():
        if not template_checker.is_allowed_template(template):
            continue
        if template_checker.get_id(template) != monument_id:
            continue
        if id_count:
            id_count += 1
            continue
        id_count = 1
        info = {
            "template": unicode(template),
            "category": commonscat_mapper.get_commonscat_from_table_row_template(template) or
                commonscat_mapper.get_commonscat_from_weblinks_template(text),
            "valid_id": template_checker.has_valid_id(template)
        }
    if info:
        info["duplicate_ids"] = id_count > 1
    else:
        info["id_not_found"] = True
    return info

def main():
    parser = argparse.ArgumentParser(description='Generate JSON info about monument data in wiki text.')
    parser.add_argument('monument_id', help='Unique ID of the monument. Validity will be checked.')
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
