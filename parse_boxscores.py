import csv
import numpy as np
from progressbar import ProgressBar
from bs4 import BeautifulSoup
from glob import glob

def parse_box_plays(soup):
    """
    Given the soup of the play-by-play page, parse out the score series.

    :soup: BeautifulSoup instance.
    :returns: A list of integers representing the scores after each play.

    """
    # Found by reading the HTML.
    play_div = soup.find_all("div", class_="stats-fullbox")[1]
    play_table = play_div.table

    # First row contains links to sets, which we don't care about.
    rows = play_table.find_all("tr")[1:]
    # All scores are inside of <td></td> tags with the "bold" class. These
    # appear to be the only things in this class here.
    scores = play_table.find_all("td", class_="bold")
    scores = [s.text for s in scores if s.text]

    # Scores are "away-home".
    score_pairs = [s.split("-") for s in scores]

    # Grab the scores we care about: OU.
    # The away name is first, then an empty column, then the home name.
    names = rows[0].find_all("th")
    away = names[0].text
    home = names[-1].text

    ou_index = 0 if away == "OU" else 1
    ou_scores = [int(s[ou_index]) for s in score_pairs]
    return ou_scores

def parse_box_statline(soup):
    """
    Given the soup of the generic boxscore page, parse out the Oglethorpe
    set statlines.

    :soup: BeautifulSoup instance.
    :returns: List of lists [kills, errors, total_attempts, pcts], where each
    inner list is the given stat per set. For example, kills[2] is the number
    of kills in the third set of the game.

    """
    # This was found by reading the HTML.
    away = soup.find("div", class_="stats-halfbox-left")
    home = soup.find("div", class_="stats-halfbox-right")
    ou_table = away if away.h4.text == "Oglethorpe" else home

    # The first row is the team name, and the second are the stat
    # abbreviations. Hence, we skip those to grab the numbers.
    sets = ou_table.find_all("tr")[2:]

    kills = []
    errors = []
    total_attempts = []
    pcts = []

    for row in sets:
        # First column is set number. Remaining columns are as listed here.
        columns = row.find_all("td")
        kill_count = int(columns[1].text)
        error_count = int(columns[2].text)
        attempts_count = int(columns[3].text)

        # Some boxscores have mistakenly left the summary statline blank. This
        # is a crude test for that. If this is the case, then skip the current
        # game.
        if attempts_count == 0:
            continue
        hit_percentage = (kill_count - error_count) / attempts_count

        kills.append(kill_count)
        errors.append(error_count)
        total_attempts.append(attempts_count)

    return [kills, errors, total_attempts, pcts]

def parse_game_score(game_score):
    """Parse a list of scores from a game into sets.

    We have two cases:

        - A team scores at least one point. Then we can simply look for when
          the next score is lower than the previous score.

        - A team scores no points. Then we have to look for a string of zeros
          that is as long as it takes to win a set. (In OU's case, this is
          _usually_ 25, but in the case of a 5th set, it is 15. In other
          competitions, it is higher or lower. We ignore this case and hope
          that OU isn't too garbage.)

    :game_score: List of scores in a game.
    :returns: A list of lists [set_1, set_2, ...], where each inner list is the
              sequence of scores for each set of the game. For example, set_2[3]
              is the Oglethorpe score after the fourth point-scoring play.

    """
    set_scores = []
    start_index = 0
    for k in range(1, len(game_score)):
        if game_score[k - 1] > game_score[k]:
            # The score has been reset, meaning that the set ended on the
            # previous score.
            set_scores.append(game_score[start_index:k])
            start_index = k

    # There is no final reset to signal the end of the game, so append the last
    # set.
    set_scores.append(game_score[start_index:])

    return set_scores

if __name__ == "__main__":
    print("Parsing boxscores...")

    kills_per_set = []
    errors_per_set = []
    attempts_per_set = []
    pcts_per_set = []

    boxscore_bar = ProgressBar()

    l = glob("./boxscores/*")
    for box_name in boxscore_bar(l):
        with open(box_name) as f:
            soup = BeautifulSoup(f.read())
            kills, errors, total_attempts, pcts = parse_box_statline(soup)
            kills_per_set += kills
            errors_per_set += errors
            attempts_per_set += total_attempts
            pcts_per_set += pcts

    print("Parsing plays...")

    play_bar = ProgressBar()

    l = glob("./plays/*")
    game_scores = []
    for play_name in play_bar(l):
        with open(play_name) as f:
            soup = BeautifulSoup(f.read())
            play_scores = parse_box_plays(soup)

            # Some sets are not correctly recorded. This is a crude test for this.
            # If this is the case, then simply skip the game.
            if len(play_scores) > 0:
                game_scores.append(play_scores)

    # 2017-09-03: I simply printed these at the interpreter and saved them to
    # vol.py.
    kills_per_set = np.array(kills_per_set)
    errors_per_set = np.array(errors_per_set)
    attempts_per_set = np.array(attempts_per_set)
    pcts_per_set = np.array(pcts_per_set)

    # Scores are too difficult for the above approach, on account of how many
    # there are. Hence we save them to a csv file, where each line corresponds
    # to OU's scores in a single set. Unfortunately, since our lines are of
    # different lengths, I don't think that numpy can do this for us quickly.
    # CSV to the rescue!

    set_scores = []

    for game_score in game_scores:
        set_scores += parse_game_score(game_score)

    with open("set_scores.csv", "w") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerows(set_scores)
