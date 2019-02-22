import math
import random

import scipy.stats as sci_stats

from settings import PROJ_DIR, team_name_mappings

from tools_file import get_overall_team_data_all, get_overall_team_data_team
from tools_file import get_season_schedule_all, get_season_schedule_team
from tools_file import get_season_odds_all, get_season_odds_team


ALL_YEARS = (2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017)


def get_non_predictive_stats(years=ALL_YEARS):
    """
    Returns stat differences without further calculations
    :param years:
    :return:
    """
    data = list()
    for year in years:
        games = get_season_schedule_all(year)
        stats = get_overall_team_data_all(year)

        for game in games:

            home = game["HOME"]
            away = game["AWAY"]

            result = dict()
            result["HOME"] = game["PTS W"] if game["WIN"] == "HOME" else game["PTS L"]
            result["AWAY"] = game["PTS W"] if game["WIN"] == "AWAY" else game["PTS L"]
            result["PTS/G Ho"] = float(stats[team_name_mappings[home]["name1"]]["OFF PTS/G"]) / float(stats[team_name_mappings[away]["name1"]]["DEF PTS/G"])
            result["PTS/G Ao"] = float(stats[team_name_mappings[away]["name1"]]["OFF PTS/G"]) / float(stats[team_name_mappings[home]["name1"]]["DEF PTS/G"])
            result["YDS/G Ho"] = float(stats[team_name_mappings[home]["name1"]]["OFF YDS/G"]) / float(stats[team_name_mappings[away]["name1"]]["DEF YDS/G"])
            result["YDS/G Ao"] = float(stats[team_name_mappings[away]["name1"]]["OFF YDS/G"]) / float(stats[team_name_mappings[home]["name1"]]["DEF YDS/G"])
            result["P YDS/G Ho"] = float(stats[team_name_mappings[home]["name1"]]["OFF P YDS/G"]) / float(stats[team_name_mappings[away]["name1"]]["DEF P YDS/G"])
            result["P YDS/G Ao"] = float(stats[team_name_mappings[away]["name1"]]["OFF P YDS/G"]) / float(stats[team_name_mappings[home]["name1"]]["DEF P YDS/G"])
            result["R YDS/G Ho"] = float(stats[team_name_mappings[home]["name1"]]["OFF R YDS/G"]) / float(stats[team_name_mappings[away]["name1"]]["DEF R YDS/G"])
            result["R YDS/G Ao"] = float(stats[team_name_mappings[away]["name1"]]["OFF R YDS/G"]) / float(stats[team_name_mappings[home]["name1"]]["DEF R YDS/G"])

            data.append(result)

    return data


def predict_season_scores_spread_correctness(years=ALL_YEARS):
    """
    Calculate the distribution of the spread correctness

    Returns an Array where each index represents the percent of predictions
        who were off by that many points (e.g. if index 10 of the array equals
        .52 then that means 52% of the predictions were 10 points off or better at
        predicting the spread)

        The last index 19 represents 19+ so it will always be equal to 1

    :param years:
    :return: Array of decimals
    """
    spreads = [0 for i in range(20)]
    count = 0
    for year in years:
        results = predict_season_scores_all(year)
        for game in results:
            count = count + 1
            actual_spread = int(game["HOME ACTUAL"]) - int(game["AWAY ACTUAL"])
            predict_spread = abs(int(game["HOME PREDICT"]) - int(game["AWAY PREDICT"]))
            difference = math.floor(abs(actual_spread - predict_spread))

            if difference > 19:
                spreads[19] += 1
            else:
                spreads[difference] += 1

    # percent_spreads = [value/count for value in spreads]
    percent_spreads = [0 for i in range(20)]
    for i in range(20):
        for j in range(19, i-1, -1):
            percent_spreads[j] += (spreads[i]/count)
    return percent_spreads


def predict_season_scores_all(year):
    """
    Returns an array of all season games for a given year
    :param year:
    :return:
    """
    schedule = get_season_schedule_all(year)
    results = list()
    for game in schedule:
        result = dict()
        result["HOME"] = game["HOME"]
        result["AWAY"] = game["AWAY"]
        result["HOME ACTUAL"] = game["PTS W"] if game["WIN"] == "HOME" else game["PTS L"]
        result["AWAY ACTUAL"] = game["PTS W"] if game["WIN"] == "AWAY" else game["PTS L"]

        predictions = heuristic_linear_regression(game["HOME"], year, game["AWAY"], year)
        result["HOME PREDICT"] = int(predictions[0])
        result["AWAY PREDICT"] = int(predictions[1])

        results.append(result)

    return results


def predict_season_scores_team(team, year):
    """
    Predict season scores for a given team and year
    :param team:
    :param year:
    :return:
    """
    schedule = get_season_schedule_team(team, year)
    results = list()
    for game in schedule:
        result = dict()
        result["HOME"] = game["HOME"]
        result["AWAY"] = game["AWAY"]
        result["HOME ACTUAL"] = game["PTS W"] if game["WIN"] == "HOME" else game["PTS L"]
        result["AWAY ACTUAL"] = game["PTS W"] if game["WIN"] == "AWAY" else game["PTS L"]

        predictions = heuristic_linear_regression(game["HOME"], year, game["AWAY"], year)
        result["HOME PREDICT"] = int(predictions[0])
        result["AWAY PREDICT"] = int(predictions[1])

        results.append(result)

    return results


# LINEAR REGRESSION ANALYSIS
def heuristic_linear_regression(team1, year1, team2, year2):
    """
    Returns the final spread of two given teams
    :param team1:
    :param year1:
    :param team2:
    :param year2:
    :return: [Team1 Score, Team2 Score]
    """
    off_score1 = linear_regression_for_stat("OFF YDS/G", team1, year1)
    def_score1 = linear_regression_for_stat("DEF YDS/G", team1, year1)
    off_score2 = linear_regression_for_stat("OFF YDS/G", team2, year2)
    def_score2 = linear_regression_for_stat("DEF YDS/G", team2, year2)

    ratio_1 = (off_score1 / def_score2)
    ratio_2 = (off_score2 / def_score1)

    result = ratio_1 / ratio_2
    result = result if ratio_1 > ratio_2 else result * -1

    off_score1 = linear_regression_for_stat("OFF PTS/G", team1, year1)
    def_score1 = linear_regression_for_stat("DEF PTS/G", team1, year1)
    off_score2 = linear_regression_for_stat("OFF PTS/G", team2, year2)
    def_score2 = linear_regression_for_stat("DEF PTS/G", team2, year2)

    team1_final = (off_score1 + def_score2) / 2
    team2_final = (off_score2 + def_score1) / 2

    factor1 = (team1_final + team2_final) / 2
    factor2 = 1

    t1 = int(factor1+(result*factor2))
    t2 = int(factor1-(result*factor2))

    return [t1, t2]


def heuristic_linear_regressionx(team1, year1, team2, year2):
    """
    Returns the final score of two given teams
    :param team1:
    :param year1:
    :param team2:
    :param year2:
    :return: [int, int]
    """
    off_score1 = linear_regression_for_stat("OFF PTS/G", team1, year1)
    def_score1 = linear_regression_for_stat("DEF PTS/G", team1, year1)
    off_score2 = linear_regression_for_stat("OFF PTS/G", team2, year2)
    def_score2 = linear_regression_for_stat("DEF PTS/G", team2, year2)

    team1_final = (off_score1 + def_score2) / 2
    team2_final = (off_score2 + def_score1) / 2

    result = [team1_final, team2_final]
    return result


def linear_regression_for_stat(stat, team, year):
    """
    Returns the linear regression for a given statistic
    :param stat:
    :param team:
    :param year:
    :return:
    """
    year1_stat = float(get_overall_team_data_team(team, year-1)[stat])
    year2_stat = float(get_overall_team_data_team(team, year-2)[stat])
    year4_stat = float(get_overall_team_data_team(team, year-4)[stat])

    y_points = [year4_stat, year2_stat, year1_stat]
    x_points = [year-4, year-2, year-1]

    result = sci_stats.linregress(x_points, y_points)
    intercept = result.intercept
    slope = result.slope
    std = result.stderr

    return (slope * year) + intercept