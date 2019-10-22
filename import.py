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

for record in glynxdata:
    org_slug = None
    org_title = None
    org_desc = None

    if 'organizations' in record:
        for org in record['organizations']:
            if org['agency_type'] == "Primary":
                org_slug = re.sub("\W+", "_", org['name']).lower()
                org_title = org['name']
                org_desc = org['description']

                # We are attempting to create an organization for every package,
                # but this creates problems since the same organization will
                # usually show up more than once. This is a temporary hack to
                # prevent the script from bombing when this happens.
                try:
                    imp.create_organization(site, org_slug, org_title, org_desc)
                except:
                    pass

    if 'collections' in record:
        for col in record['collections']:
            col_slug = re.sub("\W+", "_", col['name']).lower()
            col_title = col['name']
            col_desc = col['description']

            # We are attempting to create an collections for every package,
            # but this creates problems since the same collections will
            # usually show up more than once. This is a temporary hack to
            # prevent the script from bombing when this happens.
            try:
                imp.create_collection(site, col_slug, col_title, col_desc)
            except:
                pass

    # temp archive data
    archive=str(datetime.datetime.now().isoformat())

    imp.create_dataset(site, record, org_slug, archive)

# Close report file
if args.report:
    report_file.close()
