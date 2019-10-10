# ckan-importer

This is currently just a proof of concept, but will be adapted into a tool used
to map and import GLynx data into CKAN.

## Setup

Make sure you have the virtualenv module installed on your system:

```
sudo pip install virtualenv
```

To set up the virtualenv and dependencies for this script:

```
virtualenv -p /usr/bin/python2.7 ckan-scripts
. ckan-scripts/bin/activate
git clone https://github.alaska.edu/crstephenson/ckan-importer.git
cd ckan-importer
pip install -r requirements.txt
```

## Usage

To see the parameters on running the import script:

```
./import.py -h
```
The -url to the CKAN instance and the -apikey parameters are required for the script to work.  The url points to the running CKAN site that you need to import to.  The apikey can be found from the running CKAN site under the user's dashboard on the left hand side bar at the bottom.  For importing records this should be the "admin" user.

The script expects an "export" directory with the Glynx exported data in it (json file and a directory called "files" with the attachments).

## Some example script commands...

Delete all datasets in CKAN example:
```
./import.py -delete --apikey b7dc0d43-f7c6-40f2-aaf0-480ae4382b84 --url http://ckan-dev.gina.alaska.edu
```

Import data from the Glynx export directory example:
```
./import.py --org glynx --apikey b7dc0d43-f7c6-40f2-aaf0-480ae4382b84 --url http://ckan-dev.gina.alaska.edu
```

Import data and create an import report example:
```
./import.py --org glynx --apikey b7dc0d43-f7c6-40f2-aaf0-480ae4382b84 --url http://ckan-dev.gina.alaska.edu -report
```
