#!/usr/bin/env python
import ckanapi
import argparse
import json
import import_functions as imp

parser = argparse.ArgumentParser(description='Import Glynx data into CKAN.')
parser.add_argument('--url', help='URL to the CKAN site')
parser.add_argument('--apikey', help='API key found on the CKAN user page')
parser.add_argument('--org', help='Create organization with name')
parser.add_argument('--file', help='JSON source file of Glynx data')
parser.add_argument('delete', help='Delete all datasets in the database')

args = parser.parse_args()

# get site
site = ckanapi.RemoteCKAN(
    args.url,
    apikey=args.apikey
)

# Delete datasets
if args.delete:
    print( 'Deleting all datasets!!' )
    choice = raw_input("Are you sure? (Y/n) ")
    if choice != 'Y':
        print( 'Cancelled!' )
        exit()

    imp.delete_all_datasets(site)

# Load Glynx JSON file
with open(args.file, "r") as read_file:
    glynxdata = json.load(read_file)

print type(glynxdata[1])

# Create organization if needed
if args.org:
    imp.create_organization(site, args.org)

# Parse JSON data and create datasets in CKAN
for record in glynxdata:
    imp.create_dataset(site, record, args.org)

