# Update-Bot

This bot is for updating the placeholders in lists of monuments in the German Wikipedia for the Wiki Loves Monuments 2015 competition.

## Installation

Prerequisites: Python, pip.

The paths shown here are in `~/src` but you can change them to whatever you like.

1. Clone the WLM repository: `git clone git@github.com:wmde/WikiLovesMonuments.git`.
2. Edit `user-config.py`: insert your user name and set the absolute path for the local testing.
3. Edit `local_family.py`: Replace the host name with your local testing host name.
4. Clone the pywikibot repository:
   `git clone --branch 2.0 --recursive  https://gerrit.wikimedia.org/r/pywikibot/core.git ~/src/pywikibot`
5. Install the necessary libraries:
   `pip install -r update-bot/requirements.txt`
6. Set and export the library path:
```
PYTHONPATH=$PYTHONPATH:~/src/pywikibot
export PYTHONPATH
```

## Available Bots
### listbot.py
Creates lists of the pages in the subcategories of "[Liste (Kulturdenkmale in Deutschland)][wlm_liste]". Can output plain page names (for pasting in the export form), wiki links (for creating a wiki page) and URLs to the articles.

Usage information:

```
cd WikiLovesMonuments/update-bot
python listbot.py -help
```

### stats-bot.py
Shows the template count of pages in the each of the WLM categories. This is the preparation for writing the update bot: When it's clear which templates are used for table lines, the update bot can search/replace accordingly.

The bot ignores commonly used templates and templates that occur less than 10 times. Only 100 pages in each category are sampled.

Usage:

```
cd WikiLovesMonuments/update-bot
python stats-bot.py
```

### local-demo-bot.py
Demonstrates the usage of a bot that accesses a local wiki instead of Wikipedia.
If running this bot fails, check your `user-config.py` and `local_family.py` files.


## Running Tests
The test for the `CommonscatMapper` and `TemplateReplacer` classes are standard `unittest.TestCase` classes. They can be run from the command line:

    python -m unittest test_commonscat_mapper test_template_replacer

[wlm_liste]: https://de.wikipedia.org/wiki/Kategorie:Liste_(Kulturdenkmale_in_Deutschland)
