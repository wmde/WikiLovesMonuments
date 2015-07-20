__author__ = 'Andrew Pekarek-Kostka'

import pywikibot
from collections import Counter

site = pywikibot.Site()
page_names = [
                'Liste der Kulturdenkmale in Witterda',
                'Liste der Kulturdenkmale in Wohlsborn',
                'Liste der Kulturdenkmale in Wiegendorf',
                'Liste der Kulturdenkmale in Wundersleben',
                'Liste der Kulturdenkmale in Ostramondra',
                'Liste der Kulturdenkmale in Tellingstedt',
                'Liste der Baudenkmale in Neubrandenburg'
              ]


def main():
    progress = 0
    print('Total Pages: ' + str(len(page_names)))

    results = []

    for page in page_names:
        page_content = pywikibot.Page(site, page).text
        location_start = []
        location_end = []

        progress += 1
        print('page: ' + str(progress))

        search_start = '! '
        finder_start(page_content, location_start, search_start)

        search_end = '\n'
        finder_end(page_content, location_start, search_end, location_end)

        get_string(location_start, location_end, page_content, results)

    print('\nOriginal Array:')
    print(results)
    print('\nFrequency in Array:')
    counter(results)


def finder_start(page_content, location_start, search_start):
    location = page_content.find(search_start)
    while location != -1:
        location_start.append(location)
        location = page_content.find(search_start, location + 1)


def finder_end(page_content, location_start, search_end, location_end):
    for start in location_start:
        location = page_content.find(search_end, start)
        location_end.append(location)


def get_string(location_start, location_end, page_content, results):
    x = 0
    string = '|'

    while x < len(location_start):
        content = page_content[location_start[x]:location_end[x]]

        try:
            if location_start[x] - 1 == location_end[x - 1]:
                string = string + content.split('|', 1)[-1] + '|'
            elif location_start[x + 1] == location_end[x] + 1:
                string = string + content.split('|', 1)[-1] + '|'
            if location_start[x + 1] != location_end[x] + 1:
                results.append(string)
                string = '|'
        except Exception:
            pass

        x += 1


def counter(results):
    frequency = Counter(results)
    print(frequency)


if __name__ == '__main__':
    main()
