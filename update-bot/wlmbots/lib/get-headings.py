__author__ = 'Andrew Pekarek-Kostka'
# -*- coding: utf-8 -*-

import os
import pywikibot
import collections

site = pywikibot.Site()


def main():
    for list_file in os.listdir('lists/'):
        page_names = []
        datafile = open('lists/' + list_file)
        for line in datafile.readlines():
            page_names.append(line)
        parser(page_names, list_file)


def parser(page_names, input_file):
    progress = 0
    print 'Analyzing page: ' + input_file
    print 'Total Pages: ' + str(len(page_names))

    results = []

    for page in page_names:
        page_content = pywikibot.Page(site, page.decode('utf-8')).text
        location_start = []
        location_end = []

        progress += 1
        print 'page: ' + str(progress)

        search_start = '! '
        finder_start(page_content, location_start, search_start)

        search_end = '\n'
        finder_end(page_content, location_start, search_end, location_end)

        get_string(location_start, location_end, page_content, results)

    frequency = counter(results)

    print '\nFrequency in Array: \n' + str(frequency)
    writing_file(frequency, input_file)


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

        if x == len(location_start) - 1 or location_start[x + 1] == location_end[x] + 1:
            string = string + content.split('|', 1)[-1] + '|'
        elif x == len(location_start) - 1 or location_start[x] - 1 == location_end[x - 1]:
            string = string + content.split('|', 1)[-1] + '|'
        if x == len(location_start) - 1 or location_start[x + 1] != location_end[x] + 1:
            results.append(string)
            string = '|'

        x += 1


def counter(results):
    return collections.Counter(results).most_common()


def writing_file(frequency, file_name):
    with open('formats/' + file_name, 'w') as format_file:
        for f, count in frequency:
            format_file.write('{}: {}\n'.format(f.encode('utf-8'), count))

if __name__ == '__main__':
    main()
