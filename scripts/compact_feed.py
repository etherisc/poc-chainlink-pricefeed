import argparse
import numpy as np
import pandas as pd
import sys

from datetime import datetime


def main() -> int:
    parser = argparse.ArgumentParser(description='compact csv price feed data.')
    parser.add_argument('csv_in', type=str, help='price feed csv input file name')
    parser.add_argument('csv_out', type=str, help='output csv file name')
    args = parser.parse_args()

    feed = pd.read_csv(args.csv_in)
    feedSorted = feed.sort_values('roundId')

    feedArray = []

    i = 1
    updatedAt = 0
    updatedAtMax = 0
    roundId = 0

    for row in feedSorted.index:
        data = feedSorted.loc[row]
        roundIdGap = int(data['roundId']) - roundId

        if roundIdGap > 1:
            print('# DEBUG roundId gap {}'.format(roundIdGap))
        
        roundId = int(data['roundId'])
        updatedAt = int(data['updatedAt'])
        dtAt = datetime.fromtimestamp(updatedAt, tz=None)
        dateTimeAt = dtAt.strftime('%Y-%m-%d %H:%M:%S')
        # timeAt = dtAt.strftime('%H:%M:%S')
        answer = data['answer']
        phaseId = data['phaseId']
        aggregatorRoundId = data['aggregatorRoundId']

        arrayRow = [roundId, answer, updatedAt, phaseId, aggregatorRoundId, dateTimeAt]

        if updatedAt < updatedAtMax:
            print('# DEBUG updatedAt gap {}'.format(updatedAtMax - updatedAt))
        else:
            feedArray.append(arrayRow)
            print('row {} data {}'.format(row, arrayRow))

        if updatedAt > updatedAtMax:
            updatedAtMax = updatedAt

        i += 1

    pdColumns = ['roundId', 'answer', 'updatedAt', 'phaseId', 'aggregatorRoundId', 'dateTimeAt']
    npArray = np.array(feedArray)
    feedCompressed = pd.DataFrame(data=npArray, columns=pdColumns)
    feedCompressed.to_csv(args.csv_out, index=False)

    return 0


# example command line for calling this script
# python scripts/compact_feed.py chainlink_usdc_usd_all.csv
if __name__ == '__main__':
    sys.exit(main())