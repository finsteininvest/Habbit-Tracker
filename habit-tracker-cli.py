"""habit-tracker-cli.

Programm to track habits.
Habits can be weekly or daily

"""

from tinydb import TinyDB, Query
from blessed import Terminal
import argparse
from itertools import zip_longest
import calendar
# import datetime
from dateutil.parser import parse

dayname = ["M",
           "T",
           "W",
           "T",
           "F",
           "S",
           "S"]

db = TinyDB('tracker.json')
term = Terminal()


def horizontal(text):
    """Convert horizontal to vertical text."""
    lines = ''
    for x in zip_longest(*text.split(' '), fillvalue=' '):
        lines += ' '.join(x) + '\n'
    return lines


def print_calendar(jahr, monat):
    """Output the calendar with trackers to terminal."""
    actquery = Query()
    table = db.table('activities')
    table_done = db.table('track')
    all_activities = table.all()
    cal = calendar.Calendar()
    dates = cal.monthdays2calendar(int(jahr), int(monat))
    for week in dates:
        weekline = ''
        dateline = ''
        dateline_orig = ''
        for date, weekday in week:
            if date == 0:
                date = ''
            weekline += dayname[weekday] + ' '
            dateline_orig += str(date) + ' '
        print(' ' * 20, weekline)
        dateline = horizontal(dateline_orig)
        datelines = dateline.split('\n')
        print(' ' * 20, datelines[0])
        print(' ' * 20, datelines[1])
        dateline_list = dateline_orig.split()
        for activity in all_activities:
            done_activities = table_done.search(actquery.activity ==
                                                activity['activity'])
            # print(len(done_activities))
            out_string = activity['activity'] + \
                ' (' + activity['frequency'] + ')' + ' ' * 15
            for done_activity in done_activities:
                try:
                    check_jahr, check_monat, datum_tag = \
                        done_activity['date'].split('-')
                    # print(datum_tag)
                    if check_jahr == jahr and check_monat == monat:
                        offset = dateline_list.index(datum_tag)
                        # print(offset)
                        if offset >= 0:
                            offset_col = 22 + offset * 2
                            # print(offset_col)
                            out_string = out_string[:offset_col - 1] + \
                                'X' + out_string[offset_col:]
                except ValueError:
                    # print('ValueError')
                    pass
            print(out_string)

        print('\n')
        # out_string = out_string[:offset_col]+'X'+out_string[offset_col+1:]


def add_done(what):
    """Mark an activity as done for a specific date."""
    if len(what) == 0:
        print("Error: Do not know what to update!")
        quit()
    if len(what.split(',')) != 2:
        print("Error: Date missing.")
        quit()
    activity, datum = what.split(',')
    dt = parse(datum)
    datum = dt.strftime('%Y-%m-%d')
    table = db.table('track')
    table.insert({'activity': activity, 'date': datum})


def add(what):
    """Add something to be tracked."""
    if len(what) == 0:
        print("Error: Do not know what to add!")
        quit()
    if len(what.split(',')) != 2:
        print("Error: Frequency missing.")
        quit()
    activity, frequency = what.split(',')
    item = Query()
    table = db.table('activities')
    table.upsert({'activity': activity,
                  'frequency': frequency,
                  'status': 'active'},
                 item.activity == activity)


def main(jahr, monat, kommando, what):
    """Handle commands to tracker."""
    if kommando == 'add':
        add(what)
    if kommando == 'done':
        add_done(what)
    print_calendar(jahr, monat)


if __name__ == '__main__':
    print(term.home + term.clear)
    parser = argparse.ArgumentParser(
        prog='habit-tracker-cli',
        description='Tracking habits from the command line.')
    parser.add_argument('-y', '--year', required=True, help='Year to look at.')
    parser.add_argument('-m', '--month', required=True,
                        help='Month to look at.')
    parser.add_argument('-c', '--command', required=False,
                        help='Command: add|done',
                        default='')
    parser.add_argument('-w', '--what', required=False,
                        help='What: Activity, Frequency for "add" \
                        or Activity,Date for "done"',
                        default='')
    args = parser.parse_args()
    monthName = calendar.month_name[int(args.month)]
    jahr = args.year
    outStr = monthName + ' ' + jahr
    print('Habbit Tracker\n' + outStr)
    main(jahr, args.month, args.command, args.what)
