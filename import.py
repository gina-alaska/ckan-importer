#!/usr/bin/env python
import ckanapi
import argparse
import json
import import_functions as imp
import datetime

parser = argparse.ArgumentParser(description='Import Glynx data into CKAN.')
parser.add_argument('--url', help='URL to the CKAN site')
parser.add_argument('--apikey', help='API key found on the CKAN user page')
parser.add_argument('--org', help='Create organization with name')
parser.add_argument('--file', help='JSON source file of Glynx data')
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

# Open report file
if args.report:
    report_file = open(args.file + ".report", "w")

# Load Glynx JSON file
with open(args.file, "r") as read_file:
    glynxdata = json.load(read_file)

print type(glynxdata[1])

# Create organization if needed
if args.org:
    imp.create_organization(site, args.org)

# temp archive data
archive=str(datetime.datetime.now().isoformat())

# Parse JSON data and create datasets in CKAN
for record in glynxdata:
    if args.report and len(record["title"]) > 100:
        report_file.write("Record tile is too long:\n")
        report_file.write(record["title"].encode('utf-8') + "\n")
        report_file.write("\n")
        continue

    imp.create_dataset(site, record, args.org, archive)

# Close report file
if args.report:
    report_file.close()
