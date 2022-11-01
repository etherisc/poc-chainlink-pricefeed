import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

from datetime import datetime

# https://stackoverflow.com/questions/59286254/export-time-series-plot
# https://matplotlib.org/stable/tutorials/introductory/pyplot.html
def main() -> int:
    parser = argparse.ArgumentParser(description='plot csv price feed data.')
    parser.add_argument('csv', type=str, help='compressed feed csv input file')
    parser.add_argument('png', type=str, help='plot png output file')
    parser.add_argument('--title', type=str, help='title for plot')
    args = parser.parse_args()

    feed = pd.read_csv(args.csv)
    feed['dateTime'] = feed['dateTimeAt'].apply(pd.to_datetime)
    feed.set_index('dateTime',inplace=True)
    
    ax = feed['answer'].plot(grid=True)
    # ax.set_xlim(pd.Timestamp('2022-05-01'), pd.Timestamp('2022-12-01'))
    # ax.set_ylim(95000000, 102000000)
    
    if args.title:
        plt.title(args.title)
    
    plt.xlabel('updatedAt')
    plt.ylabel('answer')
    plt.tight_layout()
    plt.savefig(args.png)

    return 0


# example command line for calling this script
# python scripts/compact_feed_csv.py chainlink_usdc_usd_all.csv
if __name__ == '__main__':
    sys.exit(main())