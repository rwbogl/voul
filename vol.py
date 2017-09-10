import matplotlib.pyplot as plt
import numpy as np
import model
import pykov

def simulate_game(max_points=25):
    """Simulate a best of 5 Oglethorpe volleyball game.

    :max_points: Number of points a set is played to.
    :returns: True if Oglethorpe wins the game, False otherwise.

    """
    ou = 0
    opp = 0

    while True:
        if ou == 3:
            return True
        if opp == 3:
            return False

        if simulate_set(max_points):
            ou += 1
        else:
            opp += 1

def simulate_set(max_points):
    """
    Simulate a set of Oglethorpe volleyball using a constructed Markov chain.

    This Markov chain probably isn't a good model for _individual_ games, but
    could have some success in predicting how a season will go.

    :max_points: Number of points to play a set to.
    :returns: True if Oglethorpe wins, False if the opponent wins.

    """
    ou = 0
    opp = 0

    state = model.chain.walk(0)[0]

    # The gist of this loop is this:
    #   Check for everything that could possibly signal that the game is over,
    #   or start another volley.
    while True:
        if ou or opp >= max_points:
            # Have to start checking for winners.
            if ou - opp >= 2:
                # OU is ahead by more than 2 over the max score; they win.
                return True
            elif opp - ou >= 2:
                # By the same reasoning, OPP has won in this case.
                return False

        # No one won, so let's try another.
        if state == "OU":
            ou += 1
        else:
            opp += 1

        state = model.chain.move(state)

def simulate_season(season_length=30):
    """TODO: Docstring for simulate_season.

    :season_length: TODO
    :returns: TODO

    """
    return [simulate_game() for k in range(season_length)]

def season_wins(n_games=30):
    """TODO: Docstring for season_wins.

    :n_games: TODO
    :returns: TODO

    """
    return sum(simulate_season(n_games))

def season_sample_histogram(n_seasons):
    """
    Plot a (probability distribution normalized) histogram of the number of
    games won in `n_seasons` simulated seasons.

    :n_seasons: TODO
    :returns: TODO

    """
    wins = [season_wins() for k in range(n_seasons)]
    plt.hist(wins, normed=True)
    plt.title("Distribution of number of season wins")
    plt.xlabel("Number of wins")
    plt.ylabel("Probability")
