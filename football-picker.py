#!/usr/bin/env python

import os
import sys
import re

week = 1

if len(sys.argv) > 1: week = int(sys.argv[1])


def system(cmd):
    print "==> %s" % cmd
    os.system(cmd)


print "Fetching data for week %d" % week
year = 2014
url = "http://www.usafootballpools.com/common/scores_schedules/nfl-weekly-schedule-scores-odds-weather-spreads.php?year=%d&gameboard_week=%d" % (year, week)
filename = "week%02d.html" % week
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
    spread = float(line.split("</B>")[-2] .split("<B>")[-1])

    # Add data point
    games.append((away, home))
    picks.append( (abs(spread), away, home, [home, away][spread > 0]) )

print "  %d games" % len(games)

# Sort low to high
picks = sorted(picks)

# Tally up ranks
picks_dict = {}
for rank, pick in enumerate(picks):
    margin, away, home, winner = pick
    picks_dict[(away, home)] = (winner, rank + 1)

# Print picks in order
print "Picks:"
lines = ["Week %d" % week, "", "AWAY,,HOME,,,PICK,RANK"]
for away, home in games:
    winner, rank = picks_dict[(away, home)]
    lines.append("%s,,%s,,,%s,%d" % (away, home, winner, rank))
    print "  %s @ %s   *%s*  %s" % (away, home, winner, rank)

# Save results
csv = "week%02d.csv" % week
print "Writing %s" % csv
open(csv, "wt").writelines("\n".join(lines))

print "Done."

