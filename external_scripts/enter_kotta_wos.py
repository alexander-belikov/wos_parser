from kotta import Kotta, KottaJob
from kotta.kotta_functions import *
from pprint import pprint
import pandas as pd

# Create a Kotta Connection using Login with Amazon credentials
# The token from Kotta is stored in the auth.file
from os.path import expanduser
konn = Kotta(open(expanduser('~/aauth/am.cert')).read())


str_script = str()
with open('./runner.sh') as f:
    str_script += f.read()

pprint(str_script)

def job_generate(year):
    str_year = str(year)
    good_out = 'good_' + str_year + '.tar.gz'
    bad_out = 'bad_' + str_year + '.tar.gz'
    logfile = 'wos_' + str_year + '.log'
    stderr = 'STDERR.txt'
    stdout = 'STDOUT.txt'
    outputs_list = [logfile, good_out, bad_out]
    print(outputs_list)
    outputs_str = ','.join(outputs_list)
    print(outputs_str)
    inputfile = 's3://klab-webofscience/raw_zipfiles/' + str_year + '_DSSHPSH.zip'
    return KottaJob(jobtype='script', jobname ='j_' + str_year,
                    outputs=outputs_str,
                    inputs=[inputfile],
                    executable='/bin/bash wos_parser.sh ' + str_year,
                    script_name='wos_parser.sh',
                    queue='Prod',
                    walltime='300',
                    script=str_script)

jobs = [(year, job_generate(year)) for year in range(1985, 1991, 1)]

year_id_list = []
for job in jobs:
    job[1].submit(konn)
    year_id_list.append((job[0], job[1].job_id))

for job in jobs:
    print('{0} {1}'.format(job[1].job_id, job[1].status(konn)))

# delay until jobs get completed
dump = []
for job in jobs:
    dump.append((job[0], job[1].job_id, job[1].outputs[0].s3_url))
pd.DataFrame(dump, columns=['year', 'job_id', 'good_file_url']).to_csv('../../data/wos/wosp_run_1985.csv')


