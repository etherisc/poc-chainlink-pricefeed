import fileinput
import sys


def main() -> int:
    print('roundId,answer,startedAt,updatedAt,answeredInRound,phaseId,aggregatorRoundId')

    for l in fileinput.input():
        line = l.rstrip()
        if line[0] != '#':
            tok = line.split(' ')
            print(','.join(tok))

    return 0


# example command line for calling this script
# cat chainlink_usdc_usd_all.txt | python scripts/feed2csv.py > chainlink_usdc_usd_all.csv
if __name__ == '__main__':
    sys.exit(main())