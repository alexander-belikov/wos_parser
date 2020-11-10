import pickle
import gzip
import gc
import json
import re


class ChunkFlusherMono:
    def __init__(self, target_prefix, chunksize, maxchunks=None, suffix=None):
        self.target_prefix = target_prefix
        self.acc = []
        self.chunk_count = 0
        self.chunksize = chunksize
        self.maxchunks = maxchunks
        self.suffix = "good" if suffix is None else suffix
        self.chunks_flushed = 0

    def flush_chunk(self):
        if len(self.acc) > 0:
            fname = f"{self.target_prefix}#{self.suffix}#{self.chunk_count}.json.gz"
            with gzip.GzipFile(fname, 'w') as fout:
                fout.write(json.dumps(self.acc, indent=4).encode('utf-8'))
                self.chunk_count += 1

    def push(self, item):
        self.acc.append(item)
        if len(self.acc) >= self.chunksize:
            self.flush_chunk()
            self.acc = []
            gc.collect()

    def stop(self):
        return self.maxchunks is not None and (self.chunk_count >= self.maxchunks)

    def items_processed(self):
        return self.chunk_count * self.chunksize + len(self.acc)


class FPSmart:
    """
    smart file pointer : acts like a normal file pointer but subs *pattern* with substitute
    """
    def __init__(self, fp, pattern, substitute="", count=0):
        self.fp = fp
        self.pattern = pattern
        self.p = re.compile(self.pattern)
        self.count = count
        self.sub = substitute

    def read(self, n):
        s = self.fp.read(n).decode()
        return self.transform(s).encode()

    def transform(self, s):
        m = self.p.search(s)
        r = self.p.sub(self.sub, s, count=self.count)
        return r

    def close(self):
        self.fp.close()