__author__ = 'Andrew Pekarek-Kostka'
# -*- coding: utf-8 -*-

import pywikibot
from collections import Counter

site = pywikibot.Site()
datafile = open('Denkmallistenliste.txt')

page_names = []

for line in datafile.readlines():
    page_names.append(line)


def main():
    progress = 0
    print('Total Pages: ' + str(len(page_names)))

    results = []

    for page in page_names:
        page_content = pywikibot.Page(site, page.decode('utf-8')).text
        location_start = []
        location_end = []

        progress += 1
        print('page: ' + str(progress))

        search_start = '! '
        finder_start(page_content, location_start, search_start)

        search_end = '\n'
        finder_end(page_content, location_start, search_end, location_end)

        get_string(location_start, location_end, page_content, results)

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
    frequency = Counter(results).most_common()
    print(frequency)
    writing_file(frequency)


def writing_file(frequency):
    file = open('results.txt', 'w')
    file.write(str(frequency))
    file.close()

if __name__ == '__main__':
    main()
