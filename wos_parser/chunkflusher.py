import pickle
import gzip
from gc import collect
import json


class ChunkFlusher:

    def __init__(self, prefix, chunksize, maxchunks, output_mode='json'):
        self.f_prefix = prefix
        self.acc = []
        self.j = 0
        self.chunksize = chunksize
        self.maxchunks = maxchunks
        self.output_mode = output_mode

    def flush_chunk(self):
        if len(self.acc) > 0:
            if self.output_mode == 'pickle':
                with gzip.open('{0}{1}.pgz'.format(self.f_prefix, self.j), 'wb') as fp:
                    pickle.dump(self.acc, fp)
            elif self.output_mode == 'json':
                jsonfilename = '{0}{1}.json.gz'.format(self.f_prefix, self.j)
                with gzip.GzipFile(jsonfilename, 'w') as fout:
                    fout.write(json.dumps(self.acc, indent=4).encode('utf-8'))

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
