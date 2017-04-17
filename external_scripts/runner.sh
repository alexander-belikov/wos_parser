#!/bin/bash

installs() {
    if [[ "$unamestr" == 'Linux' ]]; then
        lsb_release -a
        apt-get update
    fi
}

get_year() {
   year=''
    echo ../*zip &> /dev/null
    if [[ $? -eq 0 ]]
    then
    year=$(basename ../*zip | cut -c -5)
    echo $year
    else
    echo ''
    fi
}

package_name=wos_parser
data_path=../
# year=$(get_year)
year=$1
log=../wos_$year.log
cs=200000
maxchunk=None

setup_data() {
    zipfile=`ls *zip`
    echo "Found zip files" $zipfile "of size" $(du -smh $zipfile | awk '{print $1}')
    unzip $zipfile;
}

clone_repo() {
git clone https://github.com/alexander-belikov/$1.git
echo "*** list files in wos_parser :"
ls -lht ./$1
echo "*** list files in wos_parser/wos_parser :"
ls -lht ./$1/$1
cd ./$1
python3 ./setup.py install
cd ..
}

exec_driver() {
cd ./$package_name
python3 ./driver.py -s $data_path -d $data_path -y $year -l $log -c $cs -m $maxchunk
cd ..
}

post_processing() {
tar -czf good_$year.tar.gz good_$year*.pgz
tar -czf bad_$year.tar.gz bad_$year*.pgz
echo "*** tarball sizes :"
ls -lht *.tar.gz
echo "*** all files sizes :"
ls -lht *
}

# Install packages
installs
# Setup the data files
setup_data
# Clone repo from gh
clone_repo $package_name
# Execute the driver script
exec_driver
# Prepare the results
post_processing
