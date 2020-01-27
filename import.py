#!/usr/bin/env python
#
# This script expects to have an "export" directory from which to load the Glynx data from.
# This directory should have a .json file of the GLynx data and a "files" directory with the 
# exported Glynx files. All of these should be automatically created by the Glynx export 
# rake task.
#

import ckanapi
import argparse
import json
import import_functions as imp
import datetime
import os
import re

parser = argparse.ArgumentParser(description='Import Glynx data into CKAN.')
parser.add_argument('--url', help='URL to the CKAN site')
parser.add_argument('--apikey', help='API key found on the CKAN user page')
parser.add_argument('--org', help='Create organization with name')
# parser.add_argument('--file', help='JSON source file of Glynx data')
parser.add_argument('-delete', help='Delete all datasets in the database', action='store_true', default=False)
parser.add_argument('-report', help='Report and skip all records with a title longer than 100 chars.', action='store_true', default=False)

args = parser.parse_args()

# get site
site = ckanapi.RemoteCKAN(
    args.url,
    apikey=args.apikey
)

# Delete datasets if option is set
if args.delete:
    print( 'Deleting all datasets!!' )
    choice = raw_input("Are you sure? (Y/n) ")
    if choice != 'Y':
        print( 'Cancelled!' )
        exit()

    imp.delete_all_datasets(site)
    print('All datasets have been deleted.')
    exit()

# Check for export directory
if not os.path.exists("export"):
    print("I can't find the export directory!")
    exit()
    
# Open report file
if args.report:
    report_file = open("export_report.txt", "w")

# Load Glynx JSON file
for file in os.listdir("export"):
    if file.endswith(".json"):
        with open("export/" + file, "r") as read_file:
            glynxdata = json.load(read_file)

# Create organization if needed
if args.org:
    imp.create_organization(site, args.org)

# temp archive data
archive=str(datetime.datetime.now().isoformat())

# Parse JSON data and create datasets in CKAN
for record in glynxdata:
    collections = []

    if args.report and len(record["title"]) > 100:
        report_file.write("Record tile is too long:\n")
        report_file.write(record["title"].encode('utf-8') + "\n")
        report_file.write("\n")
        continue

    # parse records for collections and create groups for them.
    if 'collections' in record:
        for col in record['collections']:
            col_slug = re.sub("\W+", "-", col['name']).lower()
            col_title = col['name']
            col_desc = col['description']
            collections.append(col_slug)

            # The EPSCoR GLynx export has both an organization and collection
            # (aka group) with the name "Southeast Alaska GIS Library". CKAN
            # appears not to allow them to use the same slug, so make the group
            # slug a little different.
            if col['name'] == "Southeast Alaska GIS Library":
                col_slug = col_slug + '_group'

            # We are attempting to create an collections for every package,
            # but this creates problems since the same collections will
            # usually show up more than once. This is a temporary hack to
            # prevent the script from bombing when this happens.
            try:
                imp.create_collection(site, col_slug, col_title, col_desc)
            except:
                pass

    imp.create_dataset(site, record, args.org, archive)

# Close report file
if args.report:
    report_file.close()
