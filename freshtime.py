from refreshbooks import api as freshbooks_api
from codebase import API as CodebaseAPI
from config import FRESHBOOKS, CODEBASE

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)

f = freshbooks_api.TokenClient(
    FRESHBOOKS['domain'],
    FRESHBOOKS['token'],
    user_agent='Example/1.0'
)

c = CodebaseAPI(**CODEBASE)

entries = c.get('/be-my-guest/time_sessions').data

for entry in entries:
    print entry
    print ""
