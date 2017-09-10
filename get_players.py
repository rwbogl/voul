#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import urllib.request as req
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from progressbar import ProgressBar
from pathlib import Path

with open("./oglethorpe?view=lineup") as f:
    soup = BeautifulSoup(f.read())

# Discovered by staring at HTML.
stats_table = soup.find_all("table")[4]

# The first row is just abbreviations, so toss it. Likewise, the last two are
# totals, so toss them.
rows = stats_table.find_all("tr")[1:-2]

PLAYER_DIR = "./player_pages"

if not os.path.exists(PLAYER_DIR):
    os.makedirs(PLAYER_DIR)

player_bar = ProgressBar()

for row in player_bar(rows):
    player_link = row.a
    player_name = player_link.text.strip().replace(" ", "-")

    dir_name = PLAYER_DIR + "/" + player_name
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # Check to see if we should update this player.
    if os.path.exists(dir_name + "/" + ".updated"):
        continue

    print("\nGetting:", player_name)

    # Get career stats for every year.
    base_player_url = urljoin("http://gopetrels.com/", player_link["href"])
    player_url = base_player_url + "?view=career"

    career_text = req.urlopen(player_url).read().decode("utf8")
    print("Got request...")

    player_soup = BeautifulSoup(career_text)
    print("Soupified...")

    # Found by staring at HTML.
    career_table = player_soup.find_all("table")[3]
    print("Found table...")

    # Get rid of the header and the totals row.
    career_rows = career_table.find_all("tr")[1:-1]

    for year_row in career_rows:
        year_link = year_row.a
        year_name = year_link.text

        # The year_link initially has "?view=profile", but we don't want that.
        base_year_url = urljoin(player_url, year_link["href"])
        stop = base_year_url.find("?")
        base_year_url = base_year_url[:stop]
        year_url = base_year_url + "?view=gamelog"

        year_page = req.urlopen(year_url).read().decode("utf8")
        with open("{}/{}.html".format(dir_name, year_name), "w") as f:
            f.write(year_page)
            print("Wrote {}...".format(year_name))

    # Create the file to signify that we don't need to update this player.
    Path(dir_name + "/" + ".updated").touch()
