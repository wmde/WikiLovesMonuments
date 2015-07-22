# -*- coding: utf-8  -*-

mylang = 'de'
#family = 'wikipedia'
family = 'local'
#usernames['wikipedia']['de'] = 'WLM Update Bot'
usernames['local']['de'] = u'admin'

# For local testing
register_family_file('local', '/Users/gabi/src/wlm/update-bot/local_family.py')
family_files['local'] = '/Users/gabi/src/wlm/update-bot/local_family.py' # register_family_file is buggy, we have to assign this again
