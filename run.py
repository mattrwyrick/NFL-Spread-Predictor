from tools_analysis import ALL_YEARS, predict_season_scores_spread_correctness


def main(years=ALL_YEARS):
    """
    Runs Analysis for the given years. Check tool_analysis.py for function info.
    :param years:
    :return:
    """
    results = dict()
    for year in years:
        distribution_array = predict_season_scores_spread_correctness([year])
        results[year] = distribution_array

        print("\n\nYear: "+str(year))
        print("Pts Away From Spread\t\tCorrectly Predicted")

        for index, value in enumerate(distribution_array):
            print(str(index)+"\t\t\t"+str(value))


if __name__ == "__main__":
    local_years = [2015, 2016, 2017]   # can set years here from [2010, 2017] and partial 2018
    main(local_years)
