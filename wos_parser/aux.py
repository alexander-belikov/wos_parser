#!/usr/bin/env python

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


def main(sourcepath, destpath, global_year):

    only_gz_files = [f for f in listdir(sourcepath) if isfile(join(sourcepath, f)) and f[-3:] == '.gz']
    good = []
    bad = []

    for f in only_gz_files:
        full_f = join(sourcepath, f)
        f_degz = join(sourcepath, f[:-3])
        gunzip_file(full_f, f_degz)
        xml_remove_trivial_namespace(f_degz)
        with open(f_degz, 'rb') as f:
            good, bad = parse_wos_xml(f, global_year, good, bad)
        logging.info('{0} parsed, {1} good records, {2} bad records'.format(f, len(good), len(bad)))

    fp = gzip.open('{0}good_{1}.pgz'.format(destpath, global_year), 'wb')
    pickle.dump(good, fp)
    fp.close()

    fp = gzip.open('{0}bad_{1}.pgz'.format(destpath, global_year), 'wb')
    pickle.dump(bad, fp)
    fp.close()

