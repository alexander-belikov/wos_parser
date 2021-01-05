import argparse
import logging
from wos_parser.aux import log_levels
from wos_parser.aux import convert
from wos_parser.parse import is_int

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--source", help="source file name, expected extension xml.gz"
    )

    parser.add_argument("-t", "--target", default=None, help="target file name")

    parser.add_argument(
        "-v",
        "--verbosity",
        default="ERROR",
        help="set level of verbosity, DEBUG, INFO, WARNING, ERROR",
    )

    parser.add_argument(
        "--how",
        default="simple",
        help="simple or standard",
    )

    parser.add_argument(
        "-l",
        "--logfile",
        default=None,
        help="Logfile path. Defaults to ./source_filename.log.gz",
    )

    parser.add_argument(
        "-c",
        "--chunksize",
        default="50000",
        type=int,
        help="chunk size of output. Defaults to 50000",
    )

    parser.add_argument(
        "-m",
        "--maxchunks",
        default=None,
        help="maximum number of chunks. Defaults to None (process all)",
    )

    args = parser.parse_args()

    if is_int(args.maxchunks):
        maxchunks = int(args.maxchunks)
    else:
        maxchunks = None

    source = args.source
    target = args.target
    logfile = args.logfile
    if target is None:
        target = source.split(".")[0]
    if logfile is None:
        logfile = source.split(".")[0] + ".log"

    logging.basicConfig(
        filename=logfile,
        level=log_levels[args.verbosity],
        format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M",
    )

    convert(source, target, args.chunksize, maxchunks, how=args.how)
