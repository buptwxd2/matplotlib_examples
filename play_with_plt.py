#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os
import os.path
import pandas as pd
import pytz
from datetime import datetime
import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import numpy as np
import datetime

starting_plot_point = datetime.datetime.strptime('2019/7/20', '%Y/%m/%d')
points = 20
end_plot_point = starting_plot_point + datetime.timedelta(days=points * 7)

def main():
    hci_csv_file = './execution_report_hci.csv'

    data = pd.read_csv(hci_csv_file)
    for index, row in data.iterrows():
        date = row['Index']
        datetime_object = datetime.datetime.strptime(date, '%Y/%m/%d')
        if datetime_object.weekday() != 2:
            data.drop(index, inplace=True)
            continue

        if datetime_object < starting_plot_point or datetime_object > end_plot_point:
            data.drop(index, inplace=True)

    # date['Index'] = data['Index'].dt.strftime('%m/%d')
    data['plot_date'] = pd.to_datetime(data['Index'], format='%Y/%m/%d')
    data['date'] = pd.to_datetime(data['Index'], format='%Y/%m/%d')
    data['date'] = data['date'].dt.strftime('%m/%d')
    data = data.set_index('date')

    # preparing data
    total = data['total'].values
    total_component = data['total_component'].values
    total_regression = data['total_regression'].values
    total_longevity = data['total_longevity'].values
    index_date = data.index.values

    attempt_rate = data['attempt_rate'].values
    pass_rate = data['pass_rate'].values
    block_rate = data['block_rate'].values

    x = np.arange(len(total_component))
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(20, 6))
    ax2 = ax.twinx()

    plt.title("Limits Execution Status")
    rects1 = ax.bar(x, total_component, width, label='single_scaling_cases')
    rects2 = ax.bar(x, total_longevity, width, label='total_regression_cases', bottom=total_component)
    rects3 = ax.bar(x, total_regression, width, label='total_longevity_cases', bottom=total_component + total_longevity)
    ax.yaxis.grid(True)

    ax2.plot(attempt_rate, color='#36ABD9', marker='o', linewidth=2, label="attempt_rate")
    ax2.plot(pass_rate, color='#B8D941', marker='o', linewidth=2, label="pass_rate")
    ax2.plot(block_rate, color='#F2A35E', marker='o', linewidth=2, label="block_rate")

    # switch the yaxis
    ax.yaxis.tick_right()
    ax2.yaxis.tick_left()

    plt.xticks(x, index_date)

    ax2.set_ylim(ymin=0.0, ymax=1.05)
    vals = ax2.get_yticks()
    ax2.set_yticklabels(['{:,.2%}'.format(x) for x in vals])

    # draw the actual numbers in the Axes
    # autolabel(rects1, ax)
    # autolabel(rects2, ax)
    # autolabel(rects3, ax)
    # for p in ax.patches:
    #     ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() * .3, p.get_height() * .97), color='white', weight='bold')

    for line in ax2.lines:
        for x, y in zip(line.get_xdata(), line.get_ydata()):
            ax2.annotate('{:,.0%}'.format(y), xy=(x, y + .01), ha='center', color='lightgrey', weight='bold')


    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()

    ax.legend(h1, l1, bbox_to_anchor=(0.9, 0), loc="lower right", bbox_transform=fig.transFigure, ncol=4)
    ax2.legend(h2, l2, bbox_to_anchor=(0.12, 0), loc="lower left",  bbox_transform=fig.transFigure, ncol=4)
    # ax2.legend(h2, l2, bbox_to_anchor=(0.5, 0), loc="lower center", bbox_transform=fig.transFigure, ncol=4)

    # remove top boarder
    # ax.spines['top'].set_visible(False)
    # ax2.spines['top'].set_visible(False)

    for tick in ax.get_xticklabels():
        tick.set_rotation(30)
        text = tick.get_text()
        if text in ['07/23', '09/24', '11/26', '01/28', '03/31']:
            tick.set_color('red')
            tick.set_fontweight('semibold')

    # plot the target line
    plot_dates = data['plot_date'].values
    new_x = np.arange(len(plot_dates))
    targets = np.ones(len(plot_dates))
    all_psi = np.zeros(len(plot_dates))

    for idx, date in enumerate(plot_dates):
        psi_num_and_dates_gen = psi_num_and_dates()
        for psi, psi_date_range, psi_date_range_str in psi_num_and_dates_gen:
            if date in psi_date_range:
                break

        if list(psi_date_range).index(date) == 0:
            targets[idx] = 0
            ax2.plot([idx, idx], [0, 1])
        elif list(psi_date_range).index(date) == 7:
            targets[idx] = 0.33
        elif list(psi_date_range).index(date) == 14:
            targets[idx] = 0.66

        all_psi[idx] = psi

    # plot the targets
    ax2.plot(targets)

    # plot the psi number
    psi_dict = {}
    for idx, psi in enumerate(all_psi):
        if psi not in psi_dict:
            psi_dict[psi] = [idx]
        else:
            psi_dict[psi].append(idx)

    for psi in psi_dict:
        ax2.text(np.mean(psi_dict[psi]), 0.9, "PSI_"+ str(psi))


    for line in ax2.lines:
        for x, y in zip(line.get_xdata(), line.get_ydata()):
            ax2.annotate('{:,.0%}'.format(y), xy=(x, y + .01), ha='center', color='lightgrey', weight='bold')



    plt.show()

def autolabel(rects, ax):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='top')


def psi_num_and_dates():
    starting_date = datetime.datetime(2019, 5, 22)
    starting_date.strftime("%y/%m/%d")

    psi_num = 33
    psi_date_range = pd.date_range("3/20/2019", periods=63, freq='D')

    for _ in range(20):
        psi_num += 1
        psi_date_range += 63
        psi_date_range_str = psi_date_range.strftime("%y/%m/%d")

        yield psi_num, psi_date_range, psi_date_range_str


if __name__ == '__main__':
    main()


