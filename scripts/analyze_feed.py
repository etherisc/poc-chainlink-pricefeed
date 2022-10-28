import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

from datetime import datetime

DECIMALS = 8
TRIGGER_VALUE = 0.99
RECOVER_VALUE = 0.95
PLOT_MIN_VALUE = 0.85
MAX_DURATION = 1

def duration2str(seconds:int) -> str:
    minutes = int(seconds / 60)
    hours = int(seconds / 3600)
    days = int(seconds / 86400)

    remainingHours = hours - days * 24
    remainingMinutes = minutes - hours * 60
    remainingSeconds = seconds % 60

    return "{}d {}:{}:{}".format(days, remainingHours, remainingMinutes, remainingSeconds)


# https://stackoverflow.com/questions/59286254/export-time-series-plot
# https://matplotlib.org/stable/tutorials/introductory/pyplot.html
def main() -> int:
    parser = argparse.ArgumentParser(description='plot csv price feed data.')
    parser.add_argument('csv', type=str, help='feed csv input file')
    parser.add_argument('--decimals', type=int, default=DECIMALS, help='decimals for exchange rate resolution (int, default={})'.format(DECIMALS))
    parser.add_argument('--triggerValue', type=float, default=TRIGGER_VALUE, help='depeg trigger exchange rate (float, default={})'.format(TRIGGER_VALUE))
    parser.add_argument('--recoverValue', type=float, default=RECOVER_VALUE, help='minimal exchange rate to auto-recover (float, default={})'.format(RECOVER_VALUE))
    parser.add_argument('--maxDuration', type=int, default=MAX_DURATION, help='max days allowed below trigger (int, default={})'.format(MAX_DURATION))
    parser.add_argument('--plotMinValue', type=float, default=PLOT_MIN_VALUE, help='plot y min value (float, default={})'.format(PLOT_MIN_VALUE))
    parser.add_argument('--title', type=str, help='title for plot')
    parser.add_argument('--pngFile', type=str, default='out.png', help='plot png output file')
    args = parser.parse_args()

    feed = pd.read_csv(args.csv)
    feedSorted = feed.sort_values('roundId')

    triggerValue = int(args.triggerValue * 10 ** args.decimals)
    recoverValue = int(args.recoverValue * 10 ** args.decimals)

    print('triggerValue: {} ({})'.format(args.triggerValue, triggerValue))
    print('recoverValue: {} ({})'.format(args.recoverValue, recoverValue))

    depegs = []

    triggeredAt = 0
    triggerTicks = 0
    lastUpdatedAt = 0

    for row in feedSorted.index:
        data = feedSorted.loc[row]

        # attribute setup
        roundId = int(data['roundId'])
        answer = int(data['answer'])
        updatedAt = int(data['updatedAt'])
        dateTimeAt = data['dateTimeAt']

        # trigger kicks in
        if triggeredAt == 0 and answer <= triggerValue:
            triggeredAt = updatedAt
            triggerTicks = 0
            
            print("TRIGGER roundId {} answer {} trigger {} dateTimeAt {}".format(roundId, answer, triggerValue, dateTimeAt))

        if triggeredAt > 0:
            # not yet recovered
            if answer < recoverValue:
                triggerTicks += 1
            # recovered at or higher than min value
            else:
                depegs.append((triggeredAt, updatedAt))
                duration = updatedAt - triggeredAt
                print("RECOVER ------- {} ticks {} roundId {} answer {} dateTimeAt {}".format(duration2str(duration), triggerTicks, roundId, answer, dateTimeAt))
                triggeredAt = 0
        
        lastUpdatedAt = updatedAt
    
    if triggeredAt > 0:
        depegs.append((triggeredAt, lastUpdatedAt))
    
    feed['dateTime'] = feed['dateTimeAt'].apply(pd.to_datetime)
    feed.set_index('dateTime',inplace=True)
    
    ax = feed['answer'].plot(grid=True)
    ax.set_xlim(pd.Timestamp('2022-01-01'), pd.Timestamp('2022-11-01'))
    ax.set_ylim(int(args.plotMinValue * 100000000), 104000000)

    # draw trigger and min value lines
    ax.axhline(y=recoverValue, color='green', alpha=0.3, linestyle='-')
    ax.axhline(y=triggerValue, color='red', alpha=0.3, linestyle='--')

    # draw depeg phases
    for phase in depegs:
        fromTs = datetime.fromtimestamp(phase[0], tz=None)
        toTs = datetime.fromtimestamp(phase[1], tz=None)
        seconds = phase[1] - phase[0]

        col = 'red'
        if seconds / (24 * 3600) < args.maxDuration:
            col = 'grey'

        ax.axvspan(fromTs, toTs, color=col, alpha=0.3)

    if args.title:
        plt.title(args.title)
    
    plt.xlabel('updatedAt')
    plt.ylabel('answer')
    plt.tight_layout()
    plt.savefig(args.pngFile, dpi=150)


    return 0


# example command line for calling this script
# python scripts/compact_feed_csv.py chainlink_usdc_usd_all.csv
if __name__ == '__main__':
    sys.exit(main())