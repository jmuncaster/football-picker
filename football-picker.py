#!/usr/bin/env python

import os
import sys
import random

from datetime import datetime, timedelta

now = datetime.now()
then = datetime(2014, 9, 2)
diff = now - then
week = 1 + diff.days / 7

year = 2014
#if len(sys.argv) > 1: week = int(sys.argv[1])
#if len(sys.argv) > 2: year = int(sys.argv[2])

blanks = sys.argv[1:]

def system(cmd):
    print "==> %s" % cmd
    os.system(cmd)


print "Fetching data for week %d" % week
url = "http://www.usafootballpools.com/common/scores_schedules/nfl-weekly-schedule-scores-odds-weather-spreads.php?year=%d&gameboard_week=%d" % (year, week)
filename = "%dweek%02d.html" % (year, week)
system('curl -s "%s" -o %s' % (url, filename))

print "Parsing %s" % filename
lines = open(filename).readlines()

print "  %d lines" % len(lines)
lines = map(lambda line : line.strip(), lines)

def starts_with(x, prefix):
    N = len(prefix)
    return x[:N] == prefix

def find_prefix(lines, prefix):
    for (i, line) in enumerate(lines):
        if starts_with(line, prefix):
            return lines[i], lines[i+1:]
    return "", []

try:
    games = []
    picks = []
    while True:
        # Get away team
        line, lines = find_prefix(lines, "<!--  AWAY -->")
        if not line: break
        line, lines = find_prefix(lines, "<TD")
        away = line.split("</TD>")[-2].split("<BR>")[-1].strip()

        # Get home team
        line, lines = find_prefix(lines, "<!-- HOME -->")
        line, lines = find_prefix(lines, "<TD")
        home = line.split("</TD>")[-2].split("<BR>")[-1].strip()

        # Get spread
        line, lines = find_prefix(lines, "<TD")
        line, lines = find_prefix(lines, "<TD")
        spread_str = line.split("</B>")[-2] .split("<B>")[-1]
        if not spread_str:
            print "  WARNING: No spread for %s at %s game" % (away, home)
            print "  Looking at command-line parameters for spread..."
            if blanks:
                spread_str = blanks[0]
                blanks = blanks[1:]
                print "  ==> Got spread for %s at %s of %s. Please verify." % \
                  (away, home, spread_str)
            else:
                url = "http://www.footballlocks.com/nfl_point_spreads.shtml"
                raise Exception("""
                    Could not find spread for %s at %s.
                    Please pass the spread on command-line. You may be able to
                    find the spread at %s""" % (away, home, url))

        spread = float(spread_str)

        # Add data point
        games.append((away, home))
        r = float(random.randint(0,9)) / 100.
        picks.append( (abs(spread) + r, away, home, [home, away][spread > 0]) )

    print "  Parsed %d games." % len(games)

    # Sort low to high
    picks = sorted(picks)

    # Tally up ranks
    picks_dict = {}
    for rank, pick in enumerate(picks):
        margin, away, home, winner = pick
        picks_dict[(away, home)] = (winner, rank + 1, margin)

    # Print picks in order
    print "Picks:"
    lines = ["Week %d" % week, "", "AWAY,,HOME,,,PICK,RANK"]
    for away, home in games:
        winner, rank, margin = picks_dict[(away, home)]
        lines.append("%s,,%s,,,%s,%d" % (away, home, winner, rank))
        print "  %20s @ %20s   ==> %20s <==     (%02d)    spread=%0.2f" % (away, home, winner, rank, margin)

    # Save results
    csv = "%dweek%02d.csv" % (year, week)
    print "Writing %s" % csv
    open(csv, "wt").writelines("\n".join(lines))

except Exception as exception:
    print ""
    print "An exception occurred:"
    print exception
    print ""

print "Done."

