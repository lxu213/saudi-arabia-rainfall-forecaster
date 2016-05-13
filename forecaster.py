# rainfall forecaster

import gc
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
from scipy.misc import factorial
from scipy.optimize import curve_fit

GAGES = ['13', '61', '64', '65', '67', '68', '405', '625', '627', '628']
DATES = pd.date_range('1/28/1966', '8/9/2005')
SELECTED_GAGE = '67'


# def visualize_period_of_record(gages):
#     """
#     Returns a Figure of rainfall period of record
#     Creates a new data frame for visualization purposes
#     Replaces any rainfall value with gage indices    """
#     rainfall = get_rainfall(dates)
#     for gage in gages:
#         for i in range(len(dates)):
#             if not math.isnan(rainfall[gage][i]):
#                 rainfall[gage][i] = gages.index(gage) + 1
#
#     plt.plot(rainfall, '|')
#     plt.axis(['1/28/1966','8/9/2005', 0, len(gages)])
#     plt.suptitle('Period of Record for Saudi Arabia Rainfall Gages')
#     gages[:0] = ' '     # empty label for bottom row in plot
#     plt.yticks(np.arange(0, len(gages)+1, 1), gages)
#     plt.savefig('PeriodofRecord', format='png')


# def plot_dist(gages):
#     """
#     Plots individual gage's distribution plots
#     Requires seaborn to run
#     """
#     rainfall = get_rainfall(dates)
#     for gage in gages:
#         # mask NaN for plotting purposes
#         mask =~ np.isnan(rainfall[gage])
#         maskedgage = rainfall[gage][mask]
#         position = gages.index(gage)+1
#         plt.subplot(2, 5, position)
#         fig = sns.distplot(maskedgage, bins=150)
#         fig.set_xlim([0, 30])
#         fig.set_ylim([0, 0.3])
#     plt.ylabel('Rainfall (mm)')
#     plt.suptitle('Rainfall Depth Distribution for Saudi Arabia Rainfall Gages')
#     plt.savefig('DistributionPlot', format='png')
#
#
# def show_statistics(gages):
#     """
#     Returns a table of statistics by gage
#     """
#     rainfall = get_rainfall(dates)
#     for gage in gages:
#         stat = pd.DataFrame(rainfall[gage].describe())
#         if gages.index(gage) == 0:
#             table = stat.T
#         else:
#             table = pd.concat([stat.T, table])
#     return table.T


# def sequential_rain(dates, selected_gage):
#     """
#     Returns a dataframe indicating first, second, third, fourth day of a storm event.
#     Extent of clustering will be used to calculate monthly conditional probabilities.
#     Rain is indicated by a value of 1.
#     """
#     day1 = [0]
#     day2 = [0]
#     day3 = [0]
#     day4 = [0]
#     data = get_rainfall(dates)[selected_gage]
#
#     for row in range(1, len(data)):
#         if np.isnan(data[row-1]) and np.isnan(data[row]) == False:
#             day1.append(1)
#         else:
#             day1.append(0)
#     for row in range(1, len(data)):
#         if day1[row-1] == 1 and np.isnan(data[row]) == False:
#             day2.append(1)
#         else:
#             day2.append(0)
#     for row in range(1, len(data)):
#         if day2[row-1] == 1 and np.isnan(data[row]) == False:
#             day3.append(1)
#         else:
#             day3.append(0)
#     for row in range(1, len(data)):
#         if day3[row-1] == 1 and np.isnan(data[row]) == False:
#             day4.append(1)
#         else:
#             day4.append(0)
#
#     return pd.DataFrame({'Day1': day1, 'Day2': day2, 'Day3': day3, 'Day4': day4}, index=data.index)


def get_rainfall(dates):
    """
    Returns a data frame containing rainfall with date indices
    Fills in missing days by reindexing dates
    """
    df = pd.DataFrame.from_csv('data.csv')
    return df.reindex(dates)


def poisson_function(k, lamb):
    """
    Poisson function, parameter lamb is the fit parameter
    """
    return (lamb ** k / factorial(k)) * np.exp(-lamb)


def conditional_probability():
    """
    Returns conditional probability given month and condition
    Pulls in dataset with total number of 1st, 2nd, 3rd, and 4th day of storm events over entire POR
    Input dataset is the result of sequential_rain function condensed over the entire POR
    Builds dataframe with monthly conditional probabilities for rain on second day given rain on first day and so forth
    """
    seq_rain = pd.DataFrame.from_csv('data_cp.csv')

    # Calculate conditional probabilities for rain given the previous day of rain
    second = seq_rain['Day2'].div(seq_rain['Day1'])
    third = seq_rain['Day3'].div(seq_rain['Day2'])
    fourth = seq_rain['Day4'].div(seq_rain['Day3'])
    return pd.DataFrame({'2|1': second, '3|2': third, '4|3': fourth}, index=seq_rain.index)


def select_c_prob(conditional_probability, month, condition):
    """
    Selects conditional probability from dataframe given month and condition (2|1, 3|2, or 4|3)
    """
    subset = conditional_probability[condition]
    return subset[month]


def get_lambda(data):
    """
    Takes in dataframe of frequency of first day rain events
    Returns an array of monthly poisson lambdas
    Curve_fit function takes in callable model function and parameters to fit (xdata, ydata) and returns optimized parameters
    """
    parameters = []

    for month in xrange(1, 13):
        monthly_data = data[(data.index.month == month)]
        n, bin_edges, patches = plt.hist(monthly_data, bins=40, range=[0.05, 20], normed=True)
        bin_middles = 0.5 * (bin_edges[1:] + bin_edges[:-1])  # calculated for xdata parameter for fitting

        parameter, cov_matrix = curve_fit(poisson_function, bin_middles, n)
        parameters.append(parameter[0])

    return parameters


def select_magnitude(month, data):
    """
    Returns a magnitude randomly selected from the historical data (by month)
    Builds dataframe of monthly storm magnitudes (depths) over entire POR
    """
    mag = data.dropna()
    return random.choice(mag[(mag.index.month == month)])


def probability_of_first_day_rain(month, data, monthly_probs=None):
    """
    Returns the probability of rain following a dry day
    """
    if monthly_probs and month in monthly_probs:
        return monthly_probs[month]
    day1_rain = [0]
    for row in xrange(1, len(data)):
        if np.isnan(data[row-1]) and np.isnan(data[row]) == False:
            day1_rain.append(1)
        else:
            day1_rain.append(0)
    # Dataframe of monthly frequency of first day rain events
    first_day = pd.Series(day1_rain, index=data.index, name='Day1')
    first_day_frequency = first_day.groupby(pd.TimeGrouper(freq='M')).sum()
    lam = get_lambda(first_day_frequency)
    result = (float(np.random.poisson(lam[month])))/30
    if monthly_probs:
        monthly_probs[month] = result
    return result


def decision(probability):
    """
    Returns True or False probabilistically based on input
    """
    return random.random() < probability


if __name__ == '__main__':
    rain = []
    index = pd.date_range('1/1/2000', '1/5/2000')
    data = get_rainfall(DATES)[SELECTED_GAGE]
    conditional_probability = conditional_probability()
    monthly_probs = {}

    for day in xrange(len(index)):
        print day
        month = index[day].month

        if len(rain) < 5:
            # may contribute some bias towards rain for first four days of forecast
            probability = probability_of_first_day_rain(month, data, monthly_probs=monthly_probs)
            it_rains = decision(probability)
            if it_rains:
                rain.append(round(select_magnitude(month, data), 1))
            else:
                rain.append(0)

        elif rain[day-1] == 0:
            probability = probability_of_first_day_rain(month, data, monthly_probs=monthly_probs)
            it_rains = decision(probability)
            if it_rains:
                rain.append(round(select_magnitude(month, data), 1))
            else:
                rain.append(0)

        elif rain[day-2] == 0 and rain[day-1] != 0:
            probability = select_c_prob(conditional_probability, month, '2|1')
            it_rains = decision(probability)
            if it_rains:
                rain.append(round(select_magnitude(month, data), 1))
            else:
                rain.append(0)

        elif rain[day-3] == 0 and rain[day-2] != 0 and rain[day-1] != 0:
            probability = select_c_prob(conditional_probability, month, '3|2')
            it_rains = decision(probability)
            if it_rains:
                rain.append(round(select_magnitude(month, data), 1))
            else:
                rain.append(0)

        elif rain[day-4] == 0 and rain[day-3] != 0 and rain[day-2] != 0 and rain[day-1] != 0:
            probability = select_c_prob(conditional_probability, month, '4|3')
            it_rains = decision(probability)
            if it_rains:
                rain.append(round(select_magnitude(month, data), 1))
            else:
                rain.append(0)

        else:
            print 'Five days of rain!?'
            rain.append(0)
        gc.collect()

    print pd.Series(rain, index=index)
