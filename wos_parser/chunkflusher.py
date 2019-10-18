import pickle
import gzip
from gc import collect


class ChunkFlusher:

    def __init__(self, prefix, chunksize, maxchunks):
        self.f_prefix = prefix
        self.acc = []
        self.j = 0
        self.chunksize = chunksize
        self.maxchunks = maxchunks

    def flush_chunk(self):
        if len(self.acc) > 0:
            with gzip.open('{0}{1}.pgz'.format(self.f_prefix, self.j), 'wb') as fp:
                pickle.dump(self.acc, fp)

    def check(self):
        if len(self.acc) >= self.chunksize:
            self.flush_chunk()
            self.j += 1
            self.acc = []
            collect()

    def push(self, item):
        self.acc.append(item)
        self.check()

    def ready(self):
        if not (self.maxchunks and self.j >= self.maxchunks):
            return True
        else:
            return False

    def items_processed(self):
        return self.j*self.chunksize + len(self.acc)
