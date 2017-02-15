import pickle
import gzip

class ChunkFlusher:

    def __init__(self, prefix, chunksize):
        self.f_prefix = prefix
        self.acc = []
        self.j = 0
        self.chunksize = chunksize

    def flush_chunk(self):
        fp = gzip.open('{0}_{1}.pgz'.format(self.f_prefix, self.j), 'wb')
        pickle.dump(self.acc, fp)
        fp.close()

    def check(self):
        if len(self.acc) > self.chunksize:
            self.dump_chunk()
            self.j += 1
            self.acc = []
        else:
            self.j += 1

    def push(self, item):
        self.acc.append(item)
        self.check()
