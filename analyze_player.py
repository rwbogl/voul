#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from glob import glob
import os.path as path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

"""
analyze_player.py

This program implements functions to analyze (and assist in analyzing) player
stats.
"""

def join_years(player_dir):
    """Join the stat years for a player into one pandas dataframe.

    :player_dir: TODO
    :returns: TODO

    """
    # Sort the files by year.
    year_csvs = sorted(glob(path.join(player_dir, "*")))
    dfs = []
    master_df = pd.DataFrame()
    for csv in year_csvs:
        df = pd.read_csv(csv, parse_dates=True, index_col=0)
        master_df = master_df.append(df)

    return master_df

def get_player_dfs(player_dirs):
    """TODO: Docstring for get_player_dfs.

    :players: TODO
    :returns: TODO

    """
    df_dict = {}

    for directory in player_dirs:
        name = path.basename(path.normpath(directory))
        df = join_years(directory)
        df_dict[name] = df

    return df_dict

def get_team_df(directory, ignore_index=False):
    """Return the dataframe that contains every player on the team.

    This...probably doesn't do what we want just yet. Games won't be assigned
    the correct index unless everyone has stats on every game.

    For example: A freshman in 2017 has the first game of the 2017 season
    listed as 0, while a Sophomore might have that listed as 30. Without
    consistency, we can't reason about the data. Maybe we should learn about
    Pandas' time series features...

    2017-09-09: I have modified our parser to include dates, at the expense of
    simple plotting. Pandas understands dates very well, and it takes a gap in
    dates to mean a gap in data. This gap carries over into plots, making it
    look very bad. To fix this, we can reset the index (df.reset_index()) to
    temporarily get the 0..n index back. This allows plotting the way it worked
    before, but with one extra step. (See below in __main__.)

    For single player analysis, this is nice. For multi-player analysis, we
    will need to be careful, but having the dates is crucial.

    :directory: TODO
    :returns: TODO

    """
    glob_path = path.join(directory, "*")
    df_dict = get_player_dfs(glob(glob_path))
    master_df = pd.DataFrame()

    for name, df in df_dict.items():
        master_df = master_df.append(df, ignore_index=ignore_index)

    return master_df

def team_date_mean(team_df):
    """TODO: Docstring for team_mean.

    :team_df: TODO
    :stat: TODO
    :returns: TODO

    """
    return team_df.reset_index().groupby("Date").mean()

def team_scatter_plot(team_df_dict, x, y, filter=None):
    """TODO: Docstring for team_scatter_plot.

    :team_df_dict: TODO
    :returns: TODO

    """
    num = plt.figure()
    ax = plt.gca()
    for name, df in team_df_dict.items():
        if filter and filter(df):
            plt.plot(df[x], df[y], "o", label=name)

if __name__ == "__main__":
    # Example analysis.
    plt.style.use("ggplot")
    team_df = get_team_df("./player_stats/")

    team_df_dict = get_player_dfs(glob("./player_stats/*"))

    top_percentile = team_df["pct"].quantile(.6)
    filter_high = lambda df: df["pct"].mean() >= top_percentile
    filter_low = lambda df: len(df["pct"].dropna()) > 0 and not filter_high(df)

    team_scatter_plot(team_df_dict, "ta", "k", filter_high)
    xs = np.linspace(0, 50)
    plt.plot(xs, xs, c="k")

    plt.xlabel("Total Attempts")
    plt.ylabel("Kills")
    plt.title("Players with mean PCT above 60th percentile")
    plt.legend()

    team_scatter_plot(team_df_dict, "ta", "k", filter_low)
    xs = np.linspace(0, 45)
    plt.plot(xs, xs, c="k")

    plt.xlabel("Total Attempts")
    plt.ylabel("Kills")
    plt.title("Players with mean PCT below 60th percentile")
    plt.legend()

    plt.show()
