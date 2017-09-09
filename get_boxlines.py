from bs4 import BeautifulSoup
import urllib.request as req
import os

with open("./oglethorpe?view=gamelog") as f:
    soup = BeautifulSoup(f.read())

# Don't ask. (I just stared at HTML and went through tables until we got the
# right one.)
stats_table = soup.find_all("table")[7]

# The first row is just header information.
# The second row OF THE CURRENT (2017-09-03) FILE is useless.
rows = stats_table.find_all("tr")[2:]

BOXSCORE_DIR = "./boxscores"
PLAYS_DIR = "./plays"

if not os.path.exists(BOXSCORE_DIR):
    os.makedirs(BOXSCORE_DIR)

if not os.path.exists(PLAYS_DIR):
    os.makedirs(PLAYS_DIR)

for k, row in enumerate(rows):
    # Get the boxscore.
    # The only present link is to the boxscores.
    box_score_link = row.a

    append = os.path.basename(box_score_link["href"])
    url = "http://gopetrels.com/sports/wvball/2016-17/boxscores/" + append
    boxscore_text = req.urlopen(url).read().decode("utf8")

    # Get the play-by-play boxscore. (Thank God for statkeepers.)
    play_url = url + "?view=plays"
    play_text = req.urlopen(play_url).read().decode("utf8")

    entries = row.find_all("td")
    # This was determined by staring at HTML.
    date = entries[0].text.strip().replace(" ", "-")
    opponent = entries[1].text.strip().replace(" ", "-")
    file_name = date + "_" + opponent

    with open("{}/{}.xml".format(BOXSCORE_DIR, file_name), "w") as f:
        f.write(boxscore_text)

    with open("./{}/{}_plays.xml".format(PLAYS_DIR, file_name), "w") as f:
        f.write(play_text)

    print("{}/{}".format(k + 1, len(rows)))
