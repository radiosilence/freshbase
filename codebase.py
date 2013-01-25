import requests
import datetime
from collections import namedtuple
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup




TimeSession = namedtuple('TimeEntry', [
    'id',
    'summary',
    'minutes',
    'session_date',
    'user_id',
    'ticket_id',
    'milestone_id',
])


coerce_field = {
    'integer': lambda x: int(x),
    'date': lambda d: datetime.date(*[int(x) for x in d.split('-')]),
}
def parse_field(field):
    if not field.get('type'):
        return field.text
    return coerce_field[field.get('type')](field.text)

class APIResponse(object):
    types = {
        'time-session': TimeSession
    }

    def __init__(self, content):
        self.soup = BeautifulSoup(content, ['xml', 'lxml'])
        self.data = []
        self.soup = list(self.soup.children)[0]

    # def __iter__(self):
    #     return self

    # def next(self):
    #     return self.parse(self.soup.children.next())

    # def parse(self, child):
    #     return child


    def parse(self):
        for child in self.soup.children:
            try:
                fields = {}
                for field in child.children:
                    try:
                        fields[field.name.replace('-', '_')] = parse_field(field)
                    except AttributeError:
                        pass
                self.data.append(TimeSession(**fields))
            except AttributeError:
                pass

class API(object):
    def __init__(self, username, key, base=None):
        self.username = username
        self.key = key
        self.base = base or 'https://api3.codebasehq.com'

    def get(self, path):
        c = self.request(path).content
        r = APIResponse(c)
        r.parse()
        return r

    def request(self, path):
        return requests.get('{base}{path}'.format(
            base=self.base,
            path=path),
            auth=HTTPBasicAuth(self.username, self.key)
        )