import csv
import os

from settings import PROJ_DIR, team_name_mappings


def get_file_path(*paths):
    """
    Returns the unopened file in relation to project head directory
    :param paths: key word strings of directories
    :return:
    """
    pathway = PROJ_DIR
    for item in paths:
        pathway = os.path.join(pathway, item)
    return pathway


def get_overall_team_data_all(year):
    """
    Returns a dictionary of all teams in a given year's season stats
    :param year:
    :return:
    """
    filename = "regular%s.csv" % str(year)
    file_pathway = get_file_path("data", "TEAM", filename)
    all_stats = dict()
    with open(file_pathway, newline='') as data:
        reader = csv.DictReader(data)
        for row in reader:
            team_stats = {key.lstrip(): row[key].lstrip() for key in row}
            all_stats[team_stats["TEAM"]] = team_stats

    return all_stats


def get_overall_team_data_team(team, year):
    """
    Returns a dictionary of a teams season stats for a given year
    :param team:
    :param year:
    :return:
    """
    team = team_name_mappings[team]["name1"]
    data = get_overall_team_data_all(year)[team]
    return data


def get_season_schedule_all(year):
    """
    Returns a list of all games for a particular year
    :param year:
    :return:
    """
    filename = "regular%s.csv" % str(year)
    file_pathway = get_file_path("data", "SCHEDULE", filename)
    games = list()
    with open(file_pathway, newline='') as data:
        reader = csv.DictReader(data)
        for row in reader:
            game = {key.lstrip(): row[key].lstrip() for key in row}
            games.append(game)

    games.sort(key=lambda x: x["WEEK"])
    return games


def get_season_schedule_team(team, year):
    """
    Returns a list of all games for a team in given year
    :param team:
    :param year:
    :return:
    """
    games = get_season_schedule_all(year)
    team_games = list()
    for game in games:
        home = game["HOME"]
        away = game["AWAY"]
        if (team == home) or (team == away):
            team_games.append(game)

    return team_games


def get_season_odds_all(year):
    """
    Returns a list of all odds for games in a particular year
    :param year:
    :return:
    """
    filename = "regular%s.csv" % str(year)
    file_pathway = get_file_path("data", "BOOKIE", filename)
    games = list()
    with open(file_pathway, newline='') as data:
        reader = csv.DictReader(data)
        for row in reader:
            game = {key.lstrip(): row[key].lstrip() for key in row}
            games.append(game)

    games.sort(key=lambda x: x["WEEK"])
    return games


def get_season_odds_team(team, year):
    """
    Returns a list of all odds for games of a team in given year
    :param team:
    :param year:
    :return:
    """
    games = get_season_odds_all(year)
    team_games = list()
    for game in games:
        favorite = game["FAVORITE"]
        underdog = game["UNDERDOG"]
        if (team == underdog) or (team == favorite):
            team_games.append(game)

    return team_games

