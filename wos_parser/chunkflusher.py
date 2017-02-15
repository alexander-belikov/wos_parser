import pickle
import gzip
from gc import collect

class ChunkFlusher:

    def __init__(self, prefix, chunksize):
        self.f_prefix = prefix
        self.acc = []
        self.j = 0
        self.chunksize = chunksize

    def flush_chunk(self):
        with gzip.open('{0}{1}.pgz'.format(self.f_prefix, self.j), 'wb') as fp:
            pickle.dump(self.acc, fp)

    def check(self):
        if len(self.acc) > self.chunksize:
            self.flush_chunk()
            self.j += 1
            self.acc = []
            collect()

    def push(self, item):
        self.acc.append(item)
        self.check()

    def items_processed(self):
        return self.j*self.chunksize + len(self.acc)
