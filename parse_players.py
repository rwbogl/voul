#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from glob import glob
from progressbar import ProgressBar
from bs4 import BeautifulSoup
import os.path as path
import os
import csv

"""

parse_players.py - parse player data into year-by-year CSV files.

This program goes through the webpages saved by get_players.py and creates CSV
files for each player's statlines. Each player gets their own directory, and
every year gets its own file.

"""

STAT_DIR = "./player_stats"

if __name__ == "__main__":
    l = glob("./player_pages/*")
    player_bar = ProgressBar()

    for player_dir in player_bar(glob("./player_pages/*")):
        player_name = path.basename(path.normpath(player_dir))
        player_dir = path.join(STAT_DIR, player_name)

        if not path.exists(player_dir):
            os.makedirs(player_dir)

        years = glob(path.join("./player_pages/", player_name, "*"))

        for year_path in years:
            # For convenience, grab the year of the start of the season.
            # (Fortunately, I don't think the season ever goes beyond this...)
            year_name = path.basename(year_path)
            stop = year_name.find("-")
            year_name = year_name[:stop]

            with open(year_path) as f:
                year_text = f.read()

            soup = BeautifulSoup(year_text)

            # Found by staring at HTML.
            game_table = soup.find_all("table")[2]
            game_rows = game_table.find_all("tr")

            # Occasionally, there is a final element of the table that doesn't
            # include any stats -- usually a footnote. To detect this, we'll
            # remove any table row that has only one <td>. This isn't a very
            # rigorous check.

            row_check = lambda r: (len(r.find_all("td")) > 1 or
                                    len(r.find_all("th")) > 1)
            game_rows = [r for r in game_rows if row_check(r)]

            year_stats = []

            # The first row is the header, so those are wrapped in <th></th>
            # tags. We want that information, but we have to get it separately.

            # The first three elements are date, opponent, and result. The
            # remaining ones are stats. We want the date and states, so do some
            # work to strip the other two.
            headers = game_rows[0].find_all("th")
            header = [h.text for h in [headers[0]] + headers[3:]]
            year_stats.append(header)

            # Now get the game stats.
            for row in game_rows[1:]:
                # The first element is the date, the second the opponent, and
                # the third the result. We only want the date and stats, so
                # there is some extra work to grab the date.
                stats = row.find_all("td")
                date_tag = stats[0]
                stats = stats[3:]

                # "Empty" stats should be left empty, not given meaningless
                # symbols. At OU, the empty stats are marked with "-", so we'll
                # make those blank.
                stats = [s.text if s.text != "-" else "" for s in stats]

                # Add the date back in along with the year.
                # Date fixes: There are whitespaces and sometimes "#"s to
                # denote footmarks. This requires some complicated stripping.
                date = year_name + " " + date_tag.text.strip().strip("#").strip()
                stats = [date] + stats

                year_stats.append(stats)

            # Strip the ".html" from the year filename, then replace it with
            # ".csv".
            year_file_name = path.basename(year_path)
            extension_start = year_file_name.rfind(".")
            year = year_file_name[:extension_start]
            stat_file_name = path.join(player_dir, year + ".csv")

            with open(stat_file_name, "w") as f:
                writer = csv.writer(f, delimiter=",")
                writer.writerows(year_stats)
