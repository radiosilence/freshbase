from refreshbooks import api as freshbooks_api
from codebase import API as CodebaseAPI
from config import FRESHBOOKS, CODEBASE
f = freshbooks_api.TokenClient(
    FRESHBOOKS['domain'],
    FRESHBOOKS['token'],
    user_agent='Example/1.0'
)

c = CodebaseAPI(**CODEBASE)

time = c.get('/be-my-guest/time_sessions')

print time.data