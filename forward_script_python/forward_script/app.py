import pywikibot

from flask import Flask, request, g, redirect, render_template_string

import logging

from lib.campaign_validator import CampaignValidator
from lib.page_information import PageInformationCollector
from lib import query_builder

from wlmbots.lib.commonscat_mapper import CommonscatMapper
from wlmbots.lib.template_checker import TemplateChecker


# default configuration
COMMONS_BASE_URL = 'https://commons.wikimedia.org/'
COMMONS_API_URL = COMMONS_BASE_URL + 'w/api.php'
COMMONS_UPLOAD_URL = COMMONS_BASE_URL + 'wiki/Special:UploadWizard?'
WIKIPEDIA_API_URL = 'https://de.wikipedia.org/w/api.php'
ADDITIONAL_CATEGORIES = ['Uploaded with UploadWizard via delists']

app = Flask(__name__)
app.config.from_object(__name__)

# Set up Logging
file_handler = logging.FileHandler("app_errors.log", encoding="utf-8")
file_handler.setLevel(logging.WARNING)
app.logger.addHandler(file_handler)


def setup_instances():
    g.site_commons = pywikibot.Site("commons", "commons")
    g.site_wikipedia = pywikibot.Site("de", "wikipedia")
    g.campaign_validator = CampaignValidator(pywikibot, g.site_commons)
    checker = TemplateChecker()
    checker.load_config("config/templates.json")
    mapper = CommonscatMapper()
    mapper.load_mapping("config/commonscat_mapping.json")
    g.page_information_collector = PageInformationCollector(checker, mapper)


@app.route('/')
def index():
    return render_template_string("WLM redirect script")


@app.route('/redirect/<path:page_name>/<campaign_name>')
def redirect_to_commons(page_name, campaign_name):
    setup_instances()
    if not g.campaign_validator.is_valid_campaign(campaign_name):
        return render_template_string("Invalid campaign_name.")
    page_name = page_name.replace("+", "_")
    article = pywikibot.Page(g.site_wikipedia, page_name)
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


if __name__ == '__main__':
    app.run()

