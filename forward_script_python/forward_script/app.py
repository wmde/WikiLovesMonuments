# -*- coding: utf-8 -*-
import mwclient

from flask import Flask, request, g, redirect, render_template_string
from werkzeug.contrib.cache import SimpleCache, RedisCache
from requestlogger import WSGILogger, ApacheFormatter

import logging
from logging.handlers import RotatingFileHandler
import urllib

from lib.campaign_validator import CampaignValidator
from lib.page_information import PageInformationCollector
from lib.prefix_remover import PrefixRemover
from lib import query_builder

from wlmbots.lib.commonscat_mapper import CommonscatMapper
from wlmbots.lib.template_checker import TemplateChecker


# default configuration
COMMONS_BASE_URL = 'https://commons.wikimedia.org/'
COMMONS_API_URL = COMMONS_BASE_URL + 'w/api.php'
COMMONS_UPLOAD_URL = COMMONS_BASE_URL + 'wiki/Special:UploadWizard?'
WIKIPEDIA_API_URL = 'https://de.wikipedia.org/w/api.php'
ADDITIONAL_CATEGORIES = ['Uploaded with UploadWizard via delists']
REDIS_HOST = "localhost"
REDIS_CACHE_PREFIX = ""


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FORWARD_SCRIPT_SETTINGS', True)

# Set up error logging
file_handler = logging.FileHandler("app_errors.log", encoding="utf-8")
file_handler.setLevel(logging.WARNING)
app.logger.addHandler(file_handler)


def setup_instances():
    g.site_commons = mwclient.Site("commons.wikimedia.org")
    g.site_wikipedia = mwclient.Site("de.wikipedia.org")
    g.campaign_validator = CampaignValidator(g.site_commons)
    checker = TemplateChecker()
    checker.load_config("config/templates.json")
    mapper = CommonscatMapper()
    mapper.load_mapping("config/commonscat_mapping.json")
    g.page_information_collector = PageInformationCollector(checker, mapper)
    if app.config["REDIS_CACHE_PREFIX"]:
        g.campaign_cache = RedisCache(host=app.config["REDIS_HOST"], key_prefix=app.config["REDIS_CACHE_PREFIX"])
    else:
        g.campaign_cache = SimpleCache()


def check_if_valid_campaign(campaign_name):
    cache_key = "campaign-" + campaign_name
    valid_campaign = g.campaign_cache.get(cache_key)
    if valid_campaign is None:
        valid_campaign = g.campaign_validator.is_valid_campaign(campaign_name)
        if valid_campaign:
            timeout = 604800
        else:
            timeout = 300
        g.campaign_cache.set(cache_key, valid_campaign, timeout)
    return valid_campaign


@app.route('/')
def index():
    return render_template_string("WLM redirect script")


@app.route('/redirect/<path:page_name>/<campaign_name>')
def redirect_to_commons(page_name, campaign_name):
    setup_instances()
    if not check_if_valid_campaign(campaign_name):
        return render_template_string("Invalid campaign_name.")
    page_name_decoded = urllib.unquote(page_name).replace("+", " ")
    article = g.site_wikipedia.Pages[page_name_decoded]
    monument_id = request.args.get('id', '')
    page_information = g.page_information_collector.get_information(article, monument_id)
    app.logger.debug(page_information.__dict__)
    coordinates = {
        "lat": request.args.get('lat', ''),
        "lon": request.args.get('lon', ''),
    }
    query = query_builder.get_query(campaign_name, page_information, page_name, monument_id,
                                    coordinates, app.config["ADDITIONAL_CATEGORIES"])
    return redirect(app.config["COMMONS_UPLOAD_URL"] + query[1:])

# Set up access log
access_log_handlers = [RotatingFileHandler('access.log', maxBytes=512000000, encoding='utf-8')]
app.wsgi_app = WSGILogger(app.wsgi_app, access_log_handlers, ApacheFormatter())

# This variable can later be used by wsgi
app_without_prefix = PrefixRemover(app)

if __name__ == '__main__':
    app.run(debug=True)

