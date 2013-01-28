import requests
import datetime
import logging
from requests.auth import HTTPBasicAuth
from lxml import etree


coerces = {
    'integer': lambda x: int(x),
    'date': lambda d: datetime.date(*[int(x) for x in d.split('-')]),
}


def parse_field(field):
    if not field.get('type'):
        return field.text
    return coerces[field.get('type')](field.text)


class APIResponse(object):
    def __init__(self, content):
        self.tree = etree.fromstring(content)
        self.data = []
        self.parse()

    def parse(self):
        for child in self.tree.getchildren():
            if child == '\n':
                continue
            try:
                fields = {}
                for field in child.getchildren():
                    # import ipdb; ipdb.set_trace()
                    if field == '\n':
                        continue
                    try:
                        fields[field.tag.replace('-', '_')] = parse_field(field)
                    except AttributeError as e:
                        logging.warning("FAILED TO PARSE FIELD {} {}: {}".format(
                            repr(field), repr(child), e))
                self.data.append(fields)
            except AttributeError:
                logging.warning("FAILED TO PARSE CHILD {}: {}".format(repr(child, e)))

class API(object):
    def __init__(self, username, key, base=None):
        self.username = username
        self.key = key
        self.base = base or 'https://api3.codebasehq.com'

    def get(self, path):
        c = self.request(path).content
        r = APIResponse(c)
        return r

    def request(self, path):
        return requests.get('{base}{path}'.format(
            base=self.base,
            path=path),
            auth=HTTPBasicAuth(self.username, self.key)
        )