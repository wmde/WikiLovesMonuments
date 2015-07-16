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
   `sudo pip install httplib2`
6. Set and export the library path:
```
PYTHONPATH=$PYTHONPATH:~/src/pywikibot
export PYTHONPATH
```

## Available Bots
### listbot.py
Creates lists of the pages in the subcategories of "[Liste (Kulturdenkmale in Deutschland)][wlm_liste]". Can output plain page names (for pasting in the export form), wiki links (for creating a wiki page) and URLs to the articles.

Usage:

```
cd WikiLovesMonuments/update-bot
python listbot.py
```

### local-demo-bot.py
Demonstrates the usage of a bot that accesses a local wiki instead of Wikipedia.
If running this bot fails, check your `user-config.py` and `local_family.py` files.


[wlm_liste]: https://de.wikipedia.org/wiki/Kategorie:Liste_(Kulturdenkmale_in_Deutschland)
