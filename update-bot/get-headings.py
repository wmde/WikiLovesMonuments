import pywikibot

site = pywikibot.Site()
page_names = [
                'Liste der Kulturdenkmale in Witterda',
                'Liste der Kulturdenkmale in Wohlsborn',
                'Liste der Kulturdenkmale in Wiegendorf',
                'Liste der Kulturdenkmale in Wundersleben',
                'Liste der Kulturdenkmale in Ostramondra',
                'Liste der Kulturdenkmale in Tellingstedt'
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

        search_start = '|- style='
        finder_start(page_content, location_start, search_start)

        search_end = '\n|-'
        finder_end(page_content, location_start, search_end, location_end)

        get_string(location_start, location_end, page_content, results)

    for a in results:
        print(a + '\n')


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
    while x < len(location_start):
        results.append((page_content[location_start[x] + 36:location_end[x]]))
        x += 1

if __name__ == '__main__':
    main()
