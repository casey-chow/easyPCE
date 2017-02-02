"""
The functions needed to actually scrape the Princeton registrar.
"""
from bs4 import BeautifulSoup
import urllib
import json
import base64
import re

#: URL for course offerings feed, per
#: https://webfeeds.princeton.edu/#feed,19
FEED_URL = 'http://etcweb.princeton.edu/webfeeds/courseofferings/'

#: Options for the course offerings feed
#: https://webfeeds.princeton.edu/#feed,19
FEED_OPTS = {
    'fmt': 'json'  # output JSON instead of XML
}


def get_json(params):
    """
    Returns the course listing page for the given params.
    """
    feed_opts = FEED_OPTS.copy()
    feed_opts.update(params)

    feed_opts_enc = urllib.urlencode(feed_opts)
    request_url = FEED_URL + '?' + feed_opts_enc

    request = urllib.urlopen(request_url)
    return json.load(request)


def get_soup(base_url, params):
    """
    Returns a Beautiful Soup instance for the given url and options
    Be warned that a page existing is not a guarantee that the course
    existed in that term.
    """
    url_opts_enc = urllib.urlencode(params)
    request_url = base_url + '?' + url_opts_enc

    page = urllib.urlopen(request_url)
    return BeautifulSoup(page, 'html5lib')


#####################################################################
# WEBFEEDS-BASED SCRAPERS                                           #
#####################################################################


def scrape_term(term='all'):
    """
    Returns an list containing the term, or all terms if none specified.
    To understand the formatting used, examine sample data
    from https://webfeeds.princeton.edu/#feed,19

    For this scraper, the expected format is as follows:
        "term": [
            {
              "code": 1174,
              "suffix": "S2017",
              "name": "S16-17",
              "cal_name": "Spring 2017",
              "reg_name": "16-17 Spr",
              "start_date": "2017-02-06",
              "end_date": "2017-06-06",
              "subjects": []
            }
        ]
    """
    data = get_json({'term': str(term)})
    return data['term']


def scrape_subjects(term='all'):
    """
    Returns an list containing all subjects in a given term.
    To understand the formatting used, examine sample data
    from https://webfeeds.princeton.edu/#feed,19

    For this scraper, the expected format is as follows:
        "term": [
            {
                ...
                "subjects": [{
                    "code":"AFS",
                    "name":"African Studies",
                    "dept_code":"AFS",
                    "dept":"African Studies"
                }]
            }
        ]
    """
    data = get_json({
        'term': str(term),
        'subject': 'list',
    })
    terms = data['term']

    # Scrub to remove duplicates
    subjects = []
    seen_codes = set()

    for term in terms:
        for subject in term['subjects']:
            if subject['code'] not in seen_codes:
                subjects.append(subject)
                seen_codes.add(subject['code'])

    return subjects


def scrape_courses(term='current', subject='all'):
    """
    Returns an generator of all courses found for the given
    term. To understand the formatting used, examine sample data
    from https://webfeeds.princeton.edu/#feed,19
    """
    data = get_json({
        'term': str(term),
        'subject': str(subject),
    })

    term_name = data['term'][0]['reg_name']
    term_code = data['term'][0]['code']
    subjects = data['term'][0]['subjects']

    for subject in subjects:
        subj_name = subject['name']
        subj_code = subject['code']

        for course in subject['courses']:
            course.update(
                term_name=term_name,
                term_code=term_code,
                subj_name=subj_name,
                subj_code=subj_code,
            )
            yield course


#####################################################################
# REGISTRAR WEBSITE-BASED SCRAPERS
#####################################################################

def scrape_course_details(term, course_id):
    """
    Returns a dict of relevant information from the registrar,
    following the format of the JSON from the web feeds.
    https://webfeeds.princeton.edu/#feed,19
    """

    def get_course_addl_info(soup):
        """
        Return additional course description information from the soup,
        as a string. This information lies between the description and
        the classroom listing, exclusive.
        The idea here is that all the additional info lies between
        the description box and the schedule/classroom assignment header,
        so we just take all the html between them and return that.
        """
        timetable_children = soup.find(id=DESCRIPTION_ID).contents

        # We add 1 to start_idx to exclude the description itself.
        start_elem = soup.find(id=ADDL_INFO_START_ID)
        start_idx = timetable_children.index(start_elem) + 1
        end_elem = soup.find('strong', text=ADDL_INFO_END_CONTENTS)
        end_idx = timetable_children.index(end_elem)

        info_list = timetable_children[start_idx:end_idx]
        return ''.join([unicode(elem) for elem in info_list])

    #: Regular expression to capture the enrolled count
    ENROLL_COUNT_RE = re.compile(r'Enrolled:\s*(\d+)')
    #: Regular expression to capture the max count
    ENROLL_MAX_RE = re.compile(r'Limit:\s*(\d+)')

    def parse_enrollment_str(enroll_str):
        """
        Parses the enrollment listing string and returns
        the current enrollment and enrollment maximum, or
        -1 for any attribute that was not found.
        This takes a string of format "Enrolled: ## Limit: ##".
        """
        enroll_count = -1
        enroll_match = ENROLL_COUNT_RE.search(enroll_str)
        if enroll_match is not None:
            enroll_count = int(enroll_match.groups()[0])

        enroll_max = -1
        enroll_match = ENROLL_MAX_RE.search(enroll_str)
        if enroll_match is not None:
            enroll_max = int(enroll_match.groups()[0])

        return {
            'enroll_count': enroll_count,
            'enroll_max': enroll_max
        }

    #: Header text indicating start of classes listing
    CLASSES_HEADER_TEXT = re.compile('Schedule/Classroom assignment:')
    #: Attribute names for classes
    CLASSES_ATTR_NAMES = (
        'id', 'section', 'time', 'days', 'room', 'enrollment', 'status')

    def get_course_classes(soup):
        """
        Return a mapping of class numbers to relevant information. See
        CLASSES_ATTR_NAMES constant for column mappings.
        """
        # Find class assignment table
        schedule = soup.find('strong', text=CLASSES_HEADER_TEXT)
        while schedule.name != 'table':
            schedule = schedule.next_sibling
        schedule = schedule.find_all('tr')[1:]  # first row is header data

        # Iterate through classes and collect information
        classes = []
        for class_elem in schedule:
            class_attrs = class_elem.find_all('td')
            class_attrs = [attr.get_text().strip() for attr in class_attrs]

            class_dict = dict(zip(CLASSES_ATTR_NAMES, class_attrs))
            class_dict.update(_parse_enrollment_str(class_dict['enrollment']))

            classes.append(class_dict)
        return classes

    def get_course_enroll_params(soup):
        """
        Returns whether the course is PDF or not, and whether the course is
        auditable or not. If values not found, returns None instead.
        """
        # The string containing enroll params. Should be the first <em> tag.
        enroll_params = soup.find('em').get_text().strip()

        # Test for Audit
        audit = None
        if 'No Audit' in enroll_params or 'na' in enroll_params:
            audit = False
        elif 'Audit' in enroll_params:
            audit = True

        pdf = None
        if 'No Pass/D/Fail' in enroll_params or 'npdf' in enroll_params:
            pdf = False
        elif 'P/D/F' in enroll_params:
            pdf = True

        # Test PDF Only
        pdf_only = None
        if 'P/D/F Only' in enroll_params:
            pdf_only = True

        return {
            'audit': audit,
            'pdf': pdf,
            'pdf_only': pdf_only,
        }

    def get_distribution_requirement(soup):
        """
        Returns the distribution requirement fulfilled by the course, or
        None if none.
        """
        # The distribution requirement always occurs right before the
        # course enrollment parameters.
        dist_req = soup.find('em').previous_sibling

        if type(dist_req) is not str:
            return None

        match = re.match(r'^\(([A-Z]{2,3})\)$', dist_req.strip())
        return match.groups()[0] if match else None

    #: Regexp used to identify professor ID
    PROFESSOR_ID_REGEX = re.compile(r'<a href="/course-offerings/'
                                    r'dirinfo\.xml\?uid=(\d+)"')

    def get_instructors(soup):
        """
        Returns the ID of the instructors of the course.
        """
        return PROFESSOR_ID_REGEX.findall(str(soup))

    soup = get_soup(BASE_URL, {
        'term': term,
        'courseid': course_id,
    })

    return {
        'additional_info': get_course_addl_info(soup),
        'classes': get_course_classes(soup),
        'enroll_params': get_course_enroll_params(soup),
        'dist_req': get_distribution_requirement(soup),
        'instructors': get_instructors(soup),
    }


#####################################################################
# EVALUATION WEBSITE-BASED SCRAPERS
#####################################################################


#: Base URL for course evaluations page
BASE_URL = 'https://reg-captiva.princeton.edu/chart/index.php'


def scrape_evals(term, course_id):
    """
    Returns the course evaluation stats (as a dict) and comments
    (as an array of strings) for a given course and term.
    """

    def get_eval_stats(soup):
        """
        Returns a mapping of category to average (as a float) for the given
        course.
        """
        # The eval stats are included in the element with
        # selector `#chart > input` in its value attribute, and is
        # base64 encoded as a JSON file.
        eval_stats_str = ''
        try:
            eval_stats_str = soup.find(id='chart').input['value']
        except AttributeError:
            return dict()  # no course evaluations were found

        eval_stats = json.loads(base64.b64decode(eval_stats_str))

        label_items = eval_stats['PlotArea']['XAxis']['Items']
        labels = [lbl['Text'] for lbl in label_items]

        value_items = eval_stats['PlotArea']['ListOfSeries'][0]['Items']
        values = [float(val['YValue']) for val in value_items]

        return dict(zip(labels, values))

    def get_eval_comments(soup):
        """
        Returns a list of comments on the course, as plain text.
        """
        tables = soup('table')
        if len(tables) < 6:  # no comments exist
            return []

        # Comments table is the last table on the page.
        comments = tables[-1].find_all('td')
        return [c.get_text().strip() for c in comments]

    soup = get_soup(BASE_URL, {
        'terminfo': term,
        'courseinfo': course_id,
    })

    stats = get_eval_stats(soup)
    comments = get_eval_comments(soup)

    return stats, comments

