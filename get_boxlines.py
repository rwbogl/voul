from bs4 import BeautifulSoup
import urllib.request as req
import os.path as path

with open("./oglethorpe?view=gamelog") as f:
    soup = BeautifulSoup(f.read())

# Don't ask. (I just stared at HTML and went through tables until we got the
# right one.)
stats_table = soup.find_all("table")[7]

# The first row is just header information.
# The second row OF THE CURRENT (2017-09-03) FILE is useless.
rows = stats_table.find_all("tr")[2:]

for k, row in enumerate(rows):
    # Get the boxscore.
    # The only present link is to the boxscores.
    box_score_link = row.a

    append = path.basename(box_score_link["href"])
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

    with open("./boxscores/{}.xml".format(file_name), "w") as f:
        f.write(boxscore_text)
    with open("./plays/{}_plays.xml".format(file_name), "w") as f:
        f.write(play_text)

    print("{}/{}".format(k + 1, len(rows)))
