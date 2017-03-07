import argparse
import logging
from wos_parser.aux import log_levels
from wos_parser.aux import main
from wos_parser.parse import is_int

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sourcepath',
                        default='.',
                        help='Path to data file')

    parser.add_argument('-d', '--destpath', default='.',
                        help='Folder to write data to, Default is current folder')

    parser.add_argument('-y', '--year', default='1985',
                        help='Global year setting')

    parser.add_argument('-v', '--verbosity',
                        default='ERROR',
                        help='set level of verbosity, DEBUG, INFO, WARNING, ERROR')

    parser.add_argument('-l', '--logfile',
                        default='./wos_parser.log',
                        help='Logfile path. Defaults to ./wos_parser.log')

    parser.add_argument('-c', '--chunksize',
                        default='100000', type=int,
                        help='Chunk size of output (output list size). Defaults to 100000')

    parser.add_argument('-m', '--maxchunks',
                        default='None',
                        help='Maximum number of chunks. Defaults to None')

    args = parser.parse_args()

    if is_int(args.maxchunks):
        maxchunks = int(args.maxchunks)
    else:
        maxchunks = None

    if is_int(args.year):
        year = int(args.year)
    else:
        raise ValueError('year argument not an integer')

    logging.basicConfig(filename=args.logfile, level=log_levels[args.verbosity],
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')

    main(args.sourcepath, args.destpath, year, args.chunksize, maxchunks)
