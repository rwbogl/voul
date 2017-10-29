# voul

This repository contains code to scrape data about Oglethorpe's Women's
volleyball team and analyze their performance. It reads data about the team and
players into CSV files, which it then puts into Pandas dataframes for easy
examination. There is code to create a Markov chain that simulates volleys,
which could in theory be used to predict the performance of the team.

## Data Scraping

The Oglethorpe volleyball team makes a good deal of their data publicly
available, but not in a convenient format. Thus, we scrape almost all of our
data from the team's website. The code to do this is in the files
[get_boxlines.py](./get_boxlines.py) and [get_players.py](./get_players.py).
It was written by staring at the site's HTML and hacking things together until
it worked.

My general procedure for scraping the data depends on the goal. To gather a
summary of the team and the play-by-play data, I download the [game
log](http://www.gopetrels.com/sports/wvball/2017-18/teams/oglethorpe?view=gamelog),
change the appropriate constants in [get_boxlines.py](./get_boxlines.py), then
run it. This should create a directory with webpages of each game. Then,
setting the appropriate constants in
[parse_boxscores.py](./parse_boxscores.py) and run it. This will create a CSV
of the boxscore statistics.

To gather player statistics, I follow the exact same procedure, but download
the [roster
page](http://www.gopetrels.com/sports/wvball/2017-18/teams/oglethorpe?view=profile&r=0&pos=)
instead, and use [get_players.py](./get_players.py) and
[parse_players.py](./parse_players.py).

## Model Building and Use

The file [model.py](./model.py) creates a Markov chain based on the set scores
obtained from the other files. The file [vol.py](./vol.py) uses this Markov
chain to simulate Oglethorpe volleyball games.
