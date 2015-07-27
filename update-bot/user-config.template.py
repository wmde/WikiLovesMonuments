# -*- coding: utf-8  -*-
import os

mylang = 'de'
#family = 'wikipedia'
family = 'local'
#usernames['wikipedia']['de'] = 'WLM Update Bot'
usernames['local']['de'] = u'admin'

local_filepath = os.path.join(os.path.dirname(os.path.realpath('__file__')), 'local_family.py')

# For local testing
family_files['local'] = local_filepath # register_family_file is buggy, we have to assign this again
register_family_file('local', local_filepath)