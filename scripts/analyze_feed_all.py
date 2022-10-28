import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

from datetime import datetime

DECIMALS = 8
MIN_VALUE = 0.95
MAX_DELTA = 0.015
WARN_DELTA = 0.0025

# https://stackoverflow.com/questions/59286254/export-time-series-plot
# https://matplotlib.org/stable/tutorials/introductory/pyplot.html
def main() -> int:
    parser = argparse.ArgumentParser(description='plot csv price feed data.')
    parser.add_argument('csv', type=str, help='feed csv input file')
    parser.add_argument('--decimals', type=int, default=DECIMALS, help='decimals for exchange rate resolution (int, default={})'.format(DECIMALS))
    parser.add_argument('--minValue', type=float, default=MIN_VALUE, help='lowest acceptable exchange rate (float, default={})'.format(MIN_VALUE))
    parser.add_argument('--maxDelta', type=float, default=MAX_DELTA, help='maximum delta between two consecutive values (float, default={})'.format(MAX_DELTA))
    parser.add_argument('--warnDelta', type=float, default=WARN_DELTA, help='delta between two consecutive values that triggers warning (float, default={})'.format(WARN_DELTA))
    args = parser.parse_args()

    feed = pd.read_csv(args.csv)
    feedSorted = feed.sort_values('roundId')

    answerLast = 10**args.decimals
    roundIdLast = 0
    startedAtLast = 0
    updatedAtLast = 0
    answeredInRoundLast = 0
    phaseIdLast = 0

    minValue = int(args.minValue * 10 ** args.decimals)
    maxDelta = int(args.maxDelta * 10 ** args.decimals)
    warnDelta = int(args.warnDelta * 10 ** args.decimals)

    print('minValue: {} ({})'.format(args.minValue, minValue))
    print('maxDelta: {} ({})'.format(args.maxDelta, maxDelta))
    print('warnDelta: {} ({})'.format(args.warnDelta, warnDelta))

    for row in feedSorted.index:
        data = feedSorted.loc[row]

        # attribute setup
        roundId = int(data['roundId'])
        answer = int(data['answer'])
        startedAt = int(data['startedAt'])
        updatedAt = int(data['updatedAt'])
        answeredInRound = int(data['answeredInRound'])
        phaseId = int(data['phaseId'])
        
        dtAt = datetime.fromtimestamp(updatedAt, tz=None)
        dateTimeAt = dtAt.strftime('%Y-%m-%d %H:%M:%S')

        # check convertion
        assert str(roundId) == str(data['roundId']), "ERROR str->int for roundId (found {} in roundId {}, expected {})".format(str(roundId), roundId, data)
        assert str(answer) == str(data['answer']), "ERROR str->int for answer (found {} in roundId {}, expected {})".format(str(roundId), roundId, data)
        assert str(startedAt) == str(data['startedAt']), "ERROR str->int for startedAt (found {} in roundId {}, expected {})".format(str(startedAt), roundId, data)
        assert str(updatedAt) == str(data['updatedAt']), "ERROR str->int for updatedAt (found {} in roundId {}, expected {})".format(str(updatedAt), roundId, data)
        # attribute value validation
        assert roundId > roundIdLast, "ERROR roundId not incrementing (roundId: {})".format(roundId)
        assert answer >= minValue, "ERROR answer outside bounds (roundId: {}, answer {}, minValue {})".format(roundId, answer, minValue)
        assert answeredInRound >= answeredInRoundLast, "ERROR answeredInRound not incrementing (roundId: {}, answeredInRound: {})".format(roundId, answeredInRound)
        
        if roundId == roundIdLast + 1:
            assert startedAt >= startedAtLast, "ERROR startedAt not incrementing (roundId {}, startedAt {}, startedAtLast {})".format(roundId, startedAt, startedAtLast)
            assert updatedAt >= updatedAtLast, "ERROR updatedAt not incrementing (roundId: {})".format(roundId)
            assert phaseId == phaseIdLast, "ERROR phaseId unexpectedly changed (roundId: {}, phaseId: {})".format(roundId, phaseId)
        else:            
            assert phaseId > phaseIdLast, "ERROR phaseId not incrementing (roundId: {}, phaseId: {})".format(roundId, phaseId)

        delta = abs(answer - answerLast) 
        assert delta <= maxDelta, "ERROR answer delta too big (roundId {}, delta {}, maxDelta {}, answer {}, answerLast {})".format(roundId, delta, maxDelta, answer, answerLast)

        if delta >= warnDelta:
            print("WARN large answer delta (roundId {}, delta {}, warnDelta {}, answer {}, answerLast {})".format(roundId, delta, warnDelta, answer, answerLast))

        # remember current values for next round
        roundIdLast = roundId
        answerLast = answer
        startedAtLast = startedAt
        updatedAtLast = updatedAt
        answeredInRoundLast = answeredInRound
        phaseIdLast = phaseId

    return 0


# example command line for calling this script
# python scripts/compact_feed_csv.py chainlink_usdc_usd_all.csv
if __name__ == '__main__':
    sys.exit(main())