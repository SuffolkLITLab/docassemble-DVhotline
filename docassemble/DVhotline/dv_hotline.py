import requests
from bs4 import BeautifulSoup, NavigableString

JANEDOE_SEARCH_URL = 'https://findhelp.janedoe.org/find_help/search'


def ma_dv_hotline(cityName=None, zipCode=None):
    assert((cityName or zipCode) and not (cityName and zipCode))
    text = get_search_result_text(cityName, zipCode)
    return parse_search_results(text)


def get_search_result_text(cityName, zipCode):
    data = {
        'zip': zipCode or '',
        'city': cityName or '',
        'submit': 'Search',
    }
    try:
        response = requests.post(JANEDOE_SEARCH_URL, data=data)
        response.raise_for_status()
    except requests.RequestException as e:
        print(e)
        raise
    return response.text


def is_empty_string(element):
    if isinstance(element, NavigableString):
        return element.string.strip() == ''
    return False


def parse_search_results(text):
    soup = BeautifulSoup(text, 'html.parser')
    results = []
    for article in soup.select('div.article'):
        program_name_tag = article.find('h3')
        program_name_tag.extract()
        program_name = program_name_tag.text

        link_tags = article.find_all('a')
        links = {}
        for tag in link_tags:
            tag.extract()
            links[tag.text.strip()] = tag['href']

        jdi_member_tags = article.select('em:contains("JDI Member")')
        jdi_member = bool(jdi_member_tags)
        for tag in jdi_member_tags:
            tag.extract()

        record = {
            'program_name': program_name,
            'organization_name': '',
            'links': links,
            'is_jdi_member': jdi_member,
        }

        children = [c for c in article.contents if not is_empty_string(c)]
        accumulator = []
        for child in children:
            if child.name == 'br':
                # everything in the accumulator belongs to a single field
                if len(accumulator) == 0:
                    pass
                elif len(accumulator) == 1:
                    # we think this should only happen when it's the org name
                    assert(not record['organization_name'])
                    record['organization_name'] = accumulator[0].string.strip()
                elif len(accumulator) == 2:
                    key = accumulator[0].string.strip().rstrip(':')
                    value = accumulator[1].string.strip()
                    assert(key not in record)
                    record[key] = value
                else:
                    raise RuntimeError("Unexpected number of things between linebreaks in an article")
                accumulator = []
            else:
                accumulator.append(child)

        results.append(record)
    return results
