# Wiki Loves Monuments Bots

These bots support the community of the German Wikipedia for the Wiki Loves Monuments 2015 competition.

## Installation

Prerequisites: Python, pip.

1. Clone the WLM repository: `git clone git@github.com:wmde/WikiLovesMonuments.git`.
2. Copy and edit `user-config.py`: insert your user name.
    ```
    cp user-config.template.py user-config.py
    ```
3. Copy and edit `local_family.py`: Replace the host name with your local testing host name.
    ```
    cp local_family.template.py local_family.py
    ```
4. Install the necessary libraries:
   `pip install -r requirements.txt`
5. To run tests install dev libraries (optional)
   `pip install -r dev-requirements.txt`

If calling pip directly does not work, use the following commands:

    python -m pip install -r requirements.txt
    python -m pip install -r dev-requirements.txt

## General usage information

You can get information on each bot by calling it with the `-help` parameter like this:
```
python -m wlmbots.list_bot -help
```

The default `user-config.py` points to your local Mediawiki installation. If you want to run a bot against the German Wikipedia, call it like this:

```
python -m wlmbots.list_bot -family:wikipedia -lang:de -user:"WLMUploadVorlageBot"
```

## Available Bots
### list_bot.py
Creates lists of the pages in the subcategories of "[Liste (Kulturdenkmale in Deutschland)][wlm_liste]". Can output plain page names (for pasting in the export form), wiki links (for creating a wiki page) and URLs to the articles.

### checker_bot.py
Checks the pages in the in the subcategories of "[Liste (Kulturdenkmale in Deutschland)][wlm_liste]" if they use approved templates and if the templates
have valid, unique IDs. It can create a result page from the check. The result
page uses two MediaWiki templates, [`Fehler_in_Denkmallisten_Tabellenkopf`](wiki_templates/Fehler_in_Denkmallisten_Tabellenkopf.txt) and [`Fehler_in_Denkmallisten_Tabellenzeile`](wiki_templates/Fehler_in_Denkmallisten_Tabellenzeile.txt) which must be copied into the Wiki once.

Configuration of the approved templates can be found in the file [`template_config.json`](template_config.json). It configures the names of the approved templates, the name of the ID parameter and a regular expression for validating ID parameters.

### stats_bot.py
Shows the template count of pages in the each of the WLM categories. This is the preparation for writing the update bot: When it's clear which templates are used for table lines, the update bot can search/replace accordingly.

The bot ignores commonly used templates and templates that occur less than 10 times. Only 100 pages in each category are sampled.


### local_demo_bot.py
Demonstrates the usage of a bot that accesses a local wiki instead of Wikipedia.
If running this bot fails, check your `user-config.py` and `local_family.py` files.


## Running Tests
The test cases are standard `unittest.TestCase` classes. They can be run from the command line:

    python -m unittest discover tests

You can also run individual tests like this:

   python tests/test_commonscat_mapper.py

[wlm_liste]: https://de.wikipedia.org/wiki/Kategorie:Liste_(Kulturdenkmale_in_Deutschland)
