import datetime
from refreshbooks import api as freshbooks_api
from refreshbooks.api import logging_request_encoder, logging_response_decoder
from codebase import API as CodebaseAPI
from config import FRESHBOOKS, CODEBASE
from clint.textui import puts, colored


def time_entry_text(time_entry):
    string = u'#{id}: {summary}'.format(**time_entry)
    if time_entry['ticket_id']:
        string += u' (ticket: #{ticket_id})'.format(**time_entry)
    return string


def parse_notes(string):
    return int(unicode(string).split(':')[0][1:])


def import_page(time_entries, fresh_entries):
    for time_entry in time_entries.getchildren():
        try:
            entry_id = parse_notes(time_entry.notes)
            fresh_entries[entry_id] = time_entry.time_entry_id
        except Exception as e:
            continue


def create_time_entry(f, entry):
    puts(u"[FreshBooks] Creating entry {}".format(
        time_entry_text(entry)
    ))
    try:
        f.time_entry.create(
            time_entry=dict(
                project_id=FRESHBOOKS['project_id'],
                task_id=FRESHBOOKS['task_id'],
                notes=time_entry_text(entry),
                date=entry['session_date'].strftime('%Y-%m-%d'),
                hours=(entry['minutes'] / 60.0)
            )
        )
    except Exception as e:
        puts(colored.red(u'[Freshbooks] ERROR {}'.format(e)))


def main(f, c):
    entries = c.get('/be-my-guest/time_sessions').data

    codebase_entries = filter(
        lambda e: e['user_id'] == CODEBASE['user_id'],
        entries
    )

    puts(u"[Codebase] Got {} Codebase entries".format(len(codebase_entries)))

    fresh_entry_ids = {}
    r = f.time_entry.list(
        per_page=100,
        page=1,
        project_id=FRESHBOOKS['project_id'],
    )
    time_entries = r.getchildren()[0]
    total_pages = int(time_entries.get('pages'))
    import_page(time_entries, fresh_entry_ids)
    puts(u"[FreshBooks] Got first page")
    for i in range(1, total_pages):
        r = f.time_entry.list(per_page=100, page=i + 1)
        puts(u"[FreshBooks] Got page {}".format(i + 1))
        time_entries = r.getchildren()[0]
        import_page(time_entries, fresh_entry_ids)
    for entry in codebase_entries:
        if entry['id'] in fresh_entry_ids:
            continue
        create_time_entry(f, entry)


if __name__ == '__main__':
    f = freshbooks_api.TokenClient(
        FRESHBOOKS['domain'],
        FRESHBOOKS['token'],
    )
    c = CodebaseAPI(
        username=CODEBASE['username'],
        key=CODEBASE['key']
    )
    main(f, c)
