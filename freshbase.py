from refreshbooks import api as freshbooks_api
from codebase import API as CodebaseAPI
from config import ACCOUNTS
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
        except Exception:
            continue


def create_time_entry(f, entry, project_id, task_id):
    puts(u"[FreshBooks] Creating entry {}".format(
        time_entry_text(entry)
    ))
    try:
        f.time_entry.create(
            time_entry=dict(
                project_id=project_id,
                task_id=task_id,
                notes=time_entry_text(entry),
                date=entry['session_date'].strftime('%Y-%m-%d'),
                hours=(entry['minutes'] / 60.0)
            )
        )
    except Exception as e:
        puts(colored.red(u'[Freshbooks] ERROR {}'.format(e)))


def update_account(freshbooks_config, codebase_config):
    f = freshbooks_api.TokenClient(
        freshbooks_config['domain'],
        freshbooks_config['token'],
    )
    c = CodebaseAPI(
        username=codebase_config['username'],
        key=codebase_config['key']
    )
    entries = c.get(
        '/{project_name}/time_sessions'.format(**codebase_config)
    ).data

    codebase_entries = filter(
        lambda e: e['user_id'] == codebase_config['user_id'],
        entries
    )

    puts(u"[Codebase] Got {} Codebase entries".format(len(codebase_entries)))

    fresh_entry_ids = {}
    r = f.time_entry.list(
        per_page=100,
        page=1,
        project_id=freshbooks_config['project_id'],
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
        create_time_entry(
            f,
            entry,
            freshbooks_config['project_id'],
            freshbooks_config['task_id']
        )


def main():
    for account in ACCOUNTS:
        update_account(account['freshbooks'], account['codebase'])

if __name__ == '__main__':
    main()
