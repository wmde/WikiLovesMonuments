# -*- coding: utf-8  -*-
import os

mylang = 'de'
# family = 'wikipedia'
family = 'local'
# usernames['wikipedia']['de'] = 'WLMUploadVorlageBot'
usernames['local']['de'] = u'admin'

_local_filepath = os.path.join(os.path.dirname(os.path.realpath('__file__')), 'local_family.py')

# For local testing
family_files['local'] = _local_filepath  # register_family_file is buggy, we have to assign this again
register_family_file('local', _local_filepath)

# When you store the credentials in a file
# see https://www.mediawiki.org/wiki/Manual:Pywikibot/Use_on_third-party_wikis#Bot_doesn.27t_want_to_stay_logged_in
# password_file = "secretsfile"
