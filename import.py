#!/usr/bin/env python
import ckanapi
import argparse
import json
import import_functions

parser = argparse.ArgumentParser(description='Import Glynx data into CKAN.')
parser.add_argument('--file', help='JSON source file of Glynx data')
parser.add_argument('--apikey', help='API key found on the CKAN user page')
parser.add_argument('--org', help='Create organization with name')

args = parser.parse_args()

# Load Glynx JSON file
with open(args.file, "r") as read_file:
    glynxdata = json.load(read_file)

print type(glynxdata[1])

#exit()

#site = ckanapi.RemoteCKAN(
#    'http://ckan.url',
#    apikey=args.apikey
#)

# Create organization if needed
if args.org:
    create_organization(args.org)

# Parse JSON data and create datasets in CKAN
for record in glynxdata:

