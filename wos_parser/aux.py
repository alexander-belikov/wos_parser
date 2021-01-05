import logging
import gzip
from shutil import copyfileobj
from .parse import parse_wos_xml
from .parse_simple import parse_simple
from .chunkflusher import ChunkFlusherMono, FPSmart

log_levels = {
    "DEBUG": logging.DEBUG, "INFO": logging.INFO,
    "WARNING": logging.WARNING, "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
    }


def gunzip_file(fname_in, fname_out):
    with gzip.open(fname_in, 'rb') as f_in:
        with open(fname_out, 'wb') as f_out:
            copyfileobj(f_in, f_out)


def convert(source, target, chunksize=100000, maxchunks=None, pattern=r'xmlns=\".*[^\"]\"(?=>)', how="standard"):

    target_prefix = target.split(".")[0]
    good_cf = ChunkFlusherMono(target_prefix, chunksize, maxchunks)
    if how == "standard":
        bad_cf = ChunkFlusherMono(target_prefix, chunksize, maxchunks, suffix="bad")

    if source[-2:] == "gz":
        open_foo = gzip.GzipFile
    elif source[-3:] == "xml":
        open_foo = open
    else:
        raise ValueError("Unknown file type")

    with open_foo(source, 'rb') as fp:
        if pattern:
            fps = FPSmart(fp, pattern)
        else:
            fps = fp
        if how == "standard":
            parse_wos_xml(fps, good_cf, bad_cf)
        elif how == "simple":
            parse_simple(fps, good_cf)

    # terminal flush
    good_cf.flush_chunk()
    logging.error(f"not an error : {good_cf.items_processed()} good records")
    if how == "standard":
        bad_cf.flush_chunk()
        logging.error(f"{bad_cf.items_processed()} bad records")
