#!/usr/bin/env python

import argparse
import logging
import gzip
from shutil import copyfileobj
from os import listdir
from os.path import isfile, join
from .parse import parse_wos_xml, xml_remove_trivial_namespace
import pickle

log_levels = {
    "DEBUG": logging.DEBUG, "INFO": logging.INFO,
    "WARNING": logging.WARNING, "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
    }


def gunzip_file(fname_in, fname_out):
    with gzip.open(fname_in, 'rb') as f_in:
        with open(fname_out, 'wb') as f_out:
            copyfileobj(f_in, f_out)


def main(fpath, global_year):

    only_gz_files = [f for f in listdir(fpath) if isfile(join(fpath, f)) and f[-2:] == 'gz']

    for f in only_gz_files:
        full_f = fpath + f
        f_degz = fpath + f[:-3]
        gunzip_file(full_f, f_degz)
        xml_remove_trivial_namespace(f_degz)
        with open(f_degz, 'rb') as f:
            good, bad = parse_wos_xml(f, global_year, good, bad)
        logging.info('{0} parsed, {1} good records, {2} bad records'.format(f, len(good), len(bad)))

    fp = gzip.open('{0}good_{1}.pgz'.format(fpath, global_year), 'wb')
    pickle.dump(good, fp)
    fp.close()
    fp = gzip.open('{0}bad_{1}.pgz'.format(fpath, global_year), 'wb')
    pickle.dump(bad, fp)
    fp.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sourcepath',
                        default='sample.xml',
                        help='Path to data file')

    parser.add_argument('-v', '--verbosity',
                        default='INFO',
                        help='set level of verbosity, DEBUG, INFO, WARN')

    parser.add_argument('-l', '--logfile',
                        default='./wos_parser.log',
                        help='Logfile path. Defaults to ./wos_parser.log')

    parser.add_argument('-d', '--destpath', default='.',
                        help='Folder to write data to, Default is current folder')

    parser.add_argument('-y', '--year', default='1985',
                        help='Global year setting')

    args = parser.parse_args()

    print("Processing : {0}".format(args.sourcefile))

    logging.basicConfig(filename=args.logfile, level=log_levels[args.verbosity],
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')
