import pywikibot

from flask import Flask, request, session, g, redirect, render_template_string

import logging

from lib.campaign_validator import CampaignValidator


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
    g.site_wikipedia = pywikibot.Site("wikipedia", "de")
    g.campaign_validator = CampaignValidator(pywikibot, g.site_commons)


@app.route('/')
def index():
    return render_template_string("WLM redirect script")


@app.route('/redirect/<path:page_name>/<campaign_name>')
def redirect_to_commons(page_name, campaign_name):
    setup_instances()
    if not g.campaign_validator.is_valid_campaign(campaign_name):
        return render_template_string("Invalid campaign_name.")
    return redirect(app.config["COMMONS_UPLOAD_URL"] + "campaign="+campaign_name)


if __name__ == '__main__':
    app.run()

