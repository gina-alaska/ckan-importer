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

Change the API key and example fields in `import.py`, then run this script:

```
./import.py
```
