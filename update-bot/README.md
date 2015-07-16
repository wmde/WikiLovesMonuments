# Update-Bot

This bot is for updating the placeholders in lists of monuments in the German Wikipedia for the Wiki Loves Monuments 2015 competition.

## Installation

Prerequisites: Python, pip

1. Clone this repository. Until we have a bot account, edit `user-config.py` and insert your own user name.
2. Clone the pywikibot repository (you can change the destination path):  
   `git clone --branch 2.0 --recursive  https://gerrit.wikimedia.org/r/pywikibot/core.git ~/src/pywikibot`
3. Install the necessary libraries:  
   `pip install httplib2 mwparserfromhell`
4. Set and export the library path:
   PYTHONPATH=$PYTHONPATH:~/src/pywikibot
   export PYTHONPATH
